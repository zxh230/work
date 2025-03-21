## 创建web集群

```shell
# 创建用于挂载的目录
mkdir 7_15/web/ -p
# 创建卷容器
docker create --name web --volume /root/7_15/web:/usr/local/apache2/htdocs --volume /usr/local/apache2/logs busybox:1.36
# 进行挂载
docker run --name web1 -itd -d -p 8081:80 --volumes-from web httpd:latest
docker run --name web2 -itd -d -p 8082:80 --volumes-from web httpd:latest
docker run --name web3 -itd -d -p 8083:80 --volumes-from web httpd:latest
# 更改为自己的姓名
echo zhaojiedong.com > index.html
# 验证
curl 10.15.200.241:{8081,8082,8083}
```

![image-20240715180552839](https://gitee.com/zhaojiedong/img/raw/master/image-20240715180552839.png)

## mysql

mysq镜像使用之前创建好的mysql:8镜像   [仙人指路](https://gitee.com/zhaojiedong/work/blob/master/笔记/7-22作业.md)

```shell
# 配置mysql开机自启
docker run -itd --name mysql mysql:8
docker exec -it mysql bash
vi /etc/profile.d/mysql.sh
###
#!?bin/bash
/usr/local/mysql/bin/mysqld --initialize-insecure  --user=mysql
sleep 3
/usr/local/mysql/bin/mysqld --user=mysql && bash
###
exit
# 将配置号的容器打包
docker commit mysql mysql_enabled
# 验证
docker rm -f mysql
docker run -itd --name mysql mysql_enabled:latest
```

![image-20240715220032002](https://gitee.com/zhaojiedong/img/raw/master/image-20240715220032002.png)

重新打标签

```shell
docker tag mysql_enabled:latest 10.15.200.241:5000/mysql:v1
```

配置私有仓库：

```bash
# 拉取镜像
docker pull registry:2
# 修改配置文件(docker02同理)
vim /usr/lib/systemd/system/docker.service
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112049387.png)

```bash
# 重启
systemctl daemon-reload
systemctl restart docker.service
# 安装软件包
yum -yq install openssl openssl-devel
# 检查数据包转发
sysctl -p
```

![Untitled](https://gitee.com/zhaojiedong/img/raw/master/Untitled.png)

------

如果没有（docker02同理）：

```bash
vim /etc/sysctl.conf
### 添加
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
###
```

------

```bash
# 配置openssl
vim /etc/pki/tls/openssl.cnf
```

在下方的v3_ca处添加

![](https://gitee.com/zhaojiedong/img/raw/master/202407112056792.png)

```bash
# 创建证书目录
mkdir -p /root/base7_11/certs
# 生成密钥
openssl req -newkey rsa:4096 -nodes -sha256 -keyout /root/base7_11/certs/domain.key -x509 -days 3650 -out /root/base7_11/certs/domain.cert
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112100072.png)

```bash
# 启动镜像
docker run -itd -p 443:443 --restart always --volume /opt/data/registry/:/var/lib/registry --volume /root/base7_11/certs/:/root/base7_11/certs/ -e REGISTRY_HTTP_ADDR=0.0.0.0:443 -e REGISTRY_HTTP_TLS_CERTIFICATE=/root/base7_11/certs/domain.cert -e REGISTRY_HTTP_TLS_KEY=/root/base7_11/certs/domain.key --name registry registry:2
# 访问
curl -k --key /certs/domain.key <https://10.15.200.241:443/v2/_catalog>
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112107336.png)

```bash
# 创建用户目录
mkdir -p /root/base7_11/user/
# 创建用户,此处自定义用户名密码
docker run --entrypoint htpasswd httpd:2 -Bbn zxh 123456 > /root/base7_11/user/htpasswd
# 关闭其他容器（必须删除registry容器与httpd容器，其他容器可以保留）
docker rm -f $(docker ps -qa)
# 启动镜像
docker run -itd -p 5000:5000 --restart always --volume /opt/data/registry/:/var/lib/registry --volume /root/base7_11/user/:/root/base7_11/user -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" -e REGISTRY_AUTH_HTPASSWD_PATH=/root/base7_11/user/htpasswd  --volume /root/base7_11/certs/:/root/base7_11/certs/  -e REGISTRY_HTTP_TLS_CERTIFICATE=/root/base7_11/certs/domain.cert -e REGISTRY_HTTP_TLS_KEY=/root/base7_11/certs/domain.key --name registry registry:2
```

在docker02上登录：

```bash
docker login 10.15.200.241:5000
# 用户名zxh
# 密码123456
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112114601.png)

在docker01上将mysql镜像上传至私人仓库

```shell
docker login 10.15.200.241:5000
# 用户名zxh
# 密码123456
# 上传
docker push 10.15.200.241:5000/mysql:v1
```

```shell
# 在docker02上下载镜像
docker pull 10.15.200.241:5000/mysql:v1
# 验证
docker images
```

![image-20240715222235082](https://gitee.com/zhaojiedong/img/raw/master/image-20240715222235082.png)

```shell
# 启动时使得数据持久化
docker run -itd --restart always --volume /usr/local/mysql/data --name mysql 10.15.200.241:5000/mysql:v1
docker inspect mysql
```

![image-20240716135148148](https://gitee.com/zhaojiedong/img/raw/master/image-20240716135148148.png)

```shell
cd /var/lib/docker/volumes/0e459c13d64dd47f1df9fa558eb6bc0247d097892b5bcc74cbe91bff1bd5ddb9/_data
ls
```

![image-20240716135230946](https://gitee.com/zhaojiedong/img/raw/master/image-20240716135230946.png)

## nginx

```shell
# 启动nginx0710容器
docker run -itd --name nginx nginx0710:v1.0
# 进入容器配置
docker exec -it nginx bash
# 安装sshd所需软件包
dnf -yq install passwd iproute openssh-server openssh-clients
# 更改root密码
passwd root
# 生成密钥文件
ssh-keygen -q -t rsa -b 2048 -f /etc/ssh/ssh_host_rsa_key -N ''
ssh-keygen -q -t ecdsa  -f  /etc/ssh/ssh_host_ecdsa_key -N ''
ssh-keygen -q -t dsa -f /etc/ssh/ssh_host_ed25519_key -N ''
# 更改配置文件使root用户可以ssh登录
vi /etc/ssh/sshd_config
```

|![](https://gitee.com/zhaojiedong/img/raw/master/image-20240715223030593.png)

```shell
# 在docker02上创建网页文件
mkdir nginx
echo ComeOnWT > nginx/index.html
```

```shell
# 在nginx容器中scp获取文件
scp root@10.15.200.242:/root/nginx/index.html /usr/local/nginx/html/index.html
# 退出容器验证
exit
curl 172.17.0.6
```

|![image-20240715223503206](https://gitee.com/zhaojiedong/img/raw/master/image-20240715223503206.png)

## Prometheusi

==拷贝配置到docker02,03==

```shell
scp /etc/yum.repos.d/docker-ce.repo 10.15.200.242:/etc/yum.repos.d/
scp /etc/sysctl.d/k8s.conf 10.15.200.242:/etc/sysctl.d/k8s.conf
scp /etc/docker/daemon.json 10.15.200.242:/etc/docker/daemon.json
scp /etc/yum.repos.d/docker-ce.repo 10.15.200.243:/etc/yum.repos.d/
scp /etc/sysctl.d/k8s.conf 10.15.200.243:/etc/sysctl.d/k8s.conf
scp /etc/docker/daemon.json 10.15.200.243:/etc/docker/daemon.json
```

==拉取镜像(三台虚拟机)==
拉取前在github文件中增加对应的版本号

![image-20240716011957902](https://gitee.com/zhaojiedong/img/raw/master/image-20240716011957902.png)

![image-20240716011919994](https://gitee.com/zhaojiedong/img/raw/master/image-20240716011919994.png)

busybox:1.36

nginx:1.20

nginx:1.24

nginx:1.22

nginx:latest

mysql:8.0

grafana/grafana:11.0.0

prom/node-exporter:v1.8.1

prom/prometheus:v2.53.0

php:8-apache

registry.k8s.io/metrics-server/metrics-server:v0.6.3

gcr.io/cadvisor/cadvisor:v0.47.0

kubernetesui/dashboard:v2.7.0

kubernetesui/metrics-scraper:v1.0.8

registry.k8s.io/ingress-nginx/controller:v1.8.0

registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20230407

rockylinux:9

```shell
# 拉取镜像时注意更改自己的用户（zxh230）与地区（cn-hangzhou），建议记事本替换
# 也可以去阿里云镜像站手动粘贴，分别是：cadvisor:v0.47.0 node-exporter:v1.8.1 prometheus:v2.53.0 grafana:11.0.0四个镜像
# docker03拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/zxh230/prometheus:v2.53.0 && docker pull registry.cn-hangzhou.aliyuncs.com/zxh230/grafana:11.0.0 && docker pull registry.cn-hangzhou.aliyuncs.com/zxh230/node-exporter:v1.8.1 && docker pull registry.cn-hangzhou.aliyuncs.com/zxh230/cadvisor:v0.47.0
# docker01，02拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/zxh230/node-exporter:v1.8.1 && docker pull registry.cn-hangzhou.aliyuncs.com/zxh230/cadvisor:v0.47.0
# 在docker01，02，03上启动cadvisor
docker run --volume=/:/rootfs:ro --volume=/var/run:/var/run:ro --volume=/sys:/sys:ro --volume=/var/lib/docker/:/var/lib/docker:ro --volume=/dev/disk/:/dev/disk:ro --publish=8080:8080 --detach=true --name=cadvisor --privileged registry.cn-hangzhou.aliyuncs.com/zxh230/cadvisor:v0.47.0
# 在docker01，02，03上启动node-exporter
docker run -d -p 9100:9100 --volume /proc/:/host/proc --volume /sys/:/host/sys  --name node-exporter registry.cn-hangzhou.aliyuncs.com/zxh230/node-exporter:v1.8.1 --path.procfs /host/proc --path.sysfs /host/sys --collector.filesystem.ignored-mount-points "^/(sys|proc|dev|host|etc)($$|/)"
# 在docker03上创建配置文件
vim prometheus.yml
###
global:
  scrape_interval:     15s # By default, scrape targets every 15 seconds.
  evaluation_interval: 15s # Evaluate rules every 15 seconds.
  # Attach these extra labels to all timeseries collected by this Prometheus instance.
  external_labels:
    monitor: 'codelab-monitor'
rule_files:
  - 'prometheus.rules.yml'
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['10.15.200.243:9090','10.15.200.243:8080','10.15.200.241:9100','10.15.200.241:8080','10.15.200.242:9100','10.15.200.242:8080']
###
# 启动prometheus
docker run -d -p 9090:9090 --volume /root/prometheus.yml:/etc/prometheus/prometheus.yml --name prometheus registry.cn-hangzhou.aliyuncs.com/zxh230/prometheus:v2.53.0
# 启动grafana，将密码设置为123.com
docker run -d -p 3000:3000 -e "GF_SECURITY_ADMIN_PASSWORD=123.com" registry.cn-hangzhou.aliyuncs.com/zxh230/grafana:11.0.0
```

 node-exporter验证图（docker01，02，03）(任意一台ip:9100)

|![image-20240716003602030](https://gitee.com/zhaojiedong/img/raw/master/image-20240716003602030.png)

cadvisor验证图（docker01，02，03）(任意一台ip:8080)
![image-20240716003641434](https://gitee.com/zhaojiedong/img/raw/master/image-20240716003641434.png)

### 验证服务器端是否能成功获取数据

访问服务器ip:9090

![image-20240716030034625](https://gitee.com/zhaojiedong/img/raw/master/image-20240716030034625.png)

![image-20240716030057079](https://gitee.com/zhaojiedong/img/raw/master/image-20240716030057079.png)

![image-20240716030110028](https://gitee.com/zhaojiedong/img/raw/master/image-20240716030110028.png)

显示up即可

#### 进入grafana网页页面(服务器ip:3000)

==用户名：admin==
==密码：123.com==
登录后显示：

![image-20240716003838536](https://gitee.com/zhaojiedong/img/raw/master/image-20240716003838536.png)

配置监控项：

![image-20240716003924320](https://gitee.com/zhaojiedong/img/raw/master/image-20240716003924320.png)

![image-20240716003938573](https://gitee.com/zhaojiedong/img/raw/master/image-20240716003938573.png)

==填写服务端ip以及端口==
![image-20240716004111374](https://gitee.com/zhaojiedong/img/raw/master/image-20240716004111374.png)

到最底部点击save

|![image-20240716004159896](https://gitee.com/zhaojiedong/img/raw/master/image-20240716004159896.png)

==不要退出==，点击连接跳转

![image-20240716004303807](https://gitee.com/zhaojiedong/img/raw/master/image-20240716004303807.png)

![image-20240716004326672](https://gitee.com/zhaojiedong/img/raw/master/image-20240716004326672.png)

输入21154后点击右侧蓝色load

![image-20240716004429785](https://gitee.com/zhaojiedong/img/raw/master/image-20240716004429785.png)

|![image-20240716004547505](https://gitee.com/zhaojiedong/img/raw/master/image-20240716004547505.png)

> ### ==注：此处应只有一个prometheus选项，选唯一的一项即可==
>
> ### 选择后点击下方绿色的import，红色是因为我的模板重复，请忽略
>
> ### 之后跳转到下方页面

![image-20240716004921769](https://gitee.com/zhaojiedong/img/raw/master/image-20240716004921769.png)

> ### 下划查看CUP等监控参数
>
> ### 出现容器信息即可

![image-20240716010406210](https://gitee.com/zhaojiedong/img/raw/master/image-20240716010406210.png)

#### ==重启后进入监控页面==
