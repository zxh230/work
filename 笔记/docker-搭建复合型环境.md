### 要求: 

1. 将三个docker node节点,创建 docker swarm 集群环境.node1上创建overlay2网卡:IP地址段: 50.X.Y.0/24，基于screach构建rocky9的base镜像，要求除内部命令外，可以使用dnf curl wget ipifconfg三条命令将上面的镜像上传到Node3中的私有仓库中。用户名为:自己名字，密码为:xxx

2. 使用第一题中创建的网络，docker swarm 的 replicas 模式 运行Prometheus server镜像.docker swarm 的 global 模式 运行 cadvisor 和 node-expoter 镜像。使最终可以访问node1的ip访问到 grafana 的监控页面，可以査看到三台主机上的基础信息，(注意端口映射)

3. node3创建bridge网络ip地址30.X.Y.0/24网关30.X.Y.100(bridge 网路: 本地运行容器).完成下面要求: 1、node1主机搭建NFS服务器2、将tomcat 的页面存放nfs服务器。访问物理机IP+9090 端口,可以访问到 tomcat 页面3、将mysql: 8.0中/var/lib/mysql 数据持久化到 nfs 服务器中.

4. 用上面创建的网络

   在该网络上，创建nginx:1.20容器2个，php:latest容器2个，mysql:8.0容器1个要求:访问 nqinx的ip+port可以看到php的测试页面和mysql的测试成功代码!(为RR轮训访问)

------

虚拟机：
		docker01：10.15.200.241
		docker02：10.15.200.242
		docker03：10.15.200.243

------

### 创建集群环境

```shell
# docker01服务器
docker swarm init --advertise-addr 10.15.200.241
```

![image-20240716175036175](https://gitee.com/zhaojiedong/img/raw/master/image-20240716175036175.png)

```shell
# 粘贴命令到其他服务器（docker02，03）
docker swarm join --token SWMTKN-1-04zwye6izfcoovwlv34pxpavozgyuq3yge7bmg333u5r2flqsp-6qh9lcmvn50amhekiy9lfpnpz 10.15.200.241:2377
```

![image-20240716175208708](https://gitee.com/zhaojiedong/img/raw/master/image-20240716175208708.png)

![image-20240716175219995](https://gitee.com/zhaojiedong/img/raw/master/image-20240716175219995.png)

```shell
# 创建overlay2网卡，此地选用50.0.0.0/24网段
docker network create --driver overlay --subnet 50.0.0.0/24 --gateway 50.0.0.1 net1
# 创建目录
mkdir -p 7_17/{image,user,rocky}
cd 7_17/
# 制作rockylinux镜像
yum -yq install supermin
supermin --prepare yum coreutils dnf iproute iputils vim net-tools bash wget curl tar rpm -o image/
mkdir systemd
supermin -v --build --format chroot image/ -o systemd/
cp /etc/resolv.conf systemd/etc/
echo 9 > systemd/etc/dnf/vars/releasever
# 进入系统
chroot systemd/ bash
# 进行配置
mknod -m 666 /dev/random c 1 8
mknod -m 666 /dev/unandom c 1 9
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9
exit
# 制作镜像
tar -cf rockylinux9_4.tar systemd/
# 创建空镜像
tar -cvf /dev/null |docker import - scratch
# 使用Dockerfile构建镜像
vim Dockerfile
### 
FROM scratch
LABEL  maintainer="zxh"
ADD rockylinux9_4.tar /
CMD ["/bin/bash"]
###
docker build -t rockylinux:9.4 ./
docker images
```

配置私有仓库：

私人仓库配置不准确，可以参阅 > [构建私人仓库实验报告by hj](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/docker7.docx)

```bash
# 拉取镜像
docker pull registry:2
# 创建目录
mkdir /opt/data/registry
# 修改配置文件(docker02,01同理)
vim /usr/lib/systemd/system/docker.service
# 添加
--insecure-registry 10.15.200.243:5000
```

图片仅供参考

![图片仅供参考](https://gitee.com/zhaojiedong/img/raw/master/202407112049387.png)

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

如果没有（docker01同理）：

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
docker run -itd -p 5000:5000 -restart always --volume /opt/data/regustry:/var/lib/registry --name registry registry:2
curl 10.15.200.243:5000/v2/_catalog
# 验证所以虚拟机是否能成功访问
# 修改镜像标签验证是否能上传(在docker03上，镜像名任意，只要标签为10.15.200.243:5000/镜像名:版本 即可)
docker tag rockylinux:9.4 10.15.200.243:5000/rocky:9
docker push 10.15.200.243:5000/rocky:9
# 上传后在docker01，02上验证访问curl 10.15.200.243:5000/v2/rocyk/tags/list是否有访问结果
# 配置openssl
vim /etc/pki/tls/openssl.cnf
```

在下方的v3_ca处添加  subjectAltName = IP:10.15.200.243
图片仅参考

![](https://gitee.com/zhaojiedong/img/raw/master/202407112056792.png)

```bash
# 创建证书目录
mkdir -p /certs
# 生成密钥
openssl req -newkey rsa:4096 -nodes -sha256 -keyout /certs/domain.key -x509 -days 3650 -out /certs/domain.cert
```

![image-20240716185907596](https://gitee.com/zhaojiedong/img/raw/master/image-20240716185907596.png)

```bash
# 将之前启动的registry启动镜像
docker run -itd -p 443:443 --restart always --volume /opt/data/registry:/var/lib/registry --volume /certs/:/certs/ -e REGISTRY_HTTP_ADDR=0.0.0.0:443 -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.cert -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key --name registry registry:2
# 访问
curl -k --key /certs/domain.key "https://10.15.200.243:443/v2/_catalog"
```

![image-20240716190039026](https://gitee.com/zhaojiedong/img/raw/master/image-20240716190039026.png)

```bash
# 配置证书
mkdir -p /etc/docker/certs.d/10.15.200.243:443/
cp /certs/domain.cert /etc/docker/certs.d/10.15.200.243\:443/ca.crt
scp /certs/domain.cert 10.15.200.241:/etc/docker/certs.d/10.15.200.243\:443/ca.crt
scp /certs/domain.cert 10.15.200.242:/etc/docker/certs.d/10.15.200.243\:443/ca.crt
# 修改镜像标签
docker tag 10.15.200.243:5000/rocky:9 10.15.200.243:443/rocky:9a
# 验证是否能上传
docker push 10.15.200.243:443/rocky:9a
# 到docker01,02验证是否能访问
curl -k --key /etc/docker/certs.d/10.15.200.243\:443/ca.crt  "https://10.15.200.243:443/v2/_catalog"
# 到docker01验证是否能下载镜像
docker pull 10.15.200.243:443/rocky:9a
# 创建用户目录
mkdir -p /user
cd /user
# 创建用户,此处自定义用户名密码
docker run --entrypoint htpasswd httpd:2 -Bbn zxh 123456 > /user/htpasswd
# 关闭其他容器（必须删除registry容器，其他容器可以保留）
docker rm -f registry
# 启动镜像
docker run -itd -p 5000:5000 --restart always --volume /opt/data/registry/:/var/lib/registry --volume /user/:/user -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" -e REGISTRY_AUTH_HTPASSWD_PATH=/user/htpasswd  --volume /certs/:/certs/  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.cert -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key --name registry registry:2
```

在docker01上登录：

```shell
docker login 10.15.200.243:5000
```

![image-20240716200017793](https://gitee.com/zhaojiedong/img/raw/master/image-20240716200017793.png)

docker01上传镜像

```shell
docker tag rockylinux:9.4 10.15.200.243:5000/rocky:9
docker push 10.15.200.243:5000/rocky:9
```

如果仍然报错请参阅 > [构建私人仓库实验报告by hj](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/docker7.docx)

------

#### 部署普罗米修斯

```shell
# 最好三台虚拟机上都存在普罗米修斯，cad，node，grafana镜像
# 在manager主节点上
# 创建监听文件
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
      - targets: ['10.15.200.243:9091','10.15.200.243:8080','10.15.200.241:9100','10.15.200.241:8080','10.15.200.242:9100','10.15.200.242:8080']
###
# 保证普罗米修斯的配置文件同时存在于三台虚拟机上的相同路径，否则启动会报错
# 启动普罗米修斯
docker service create --replicas 1 --name prometheus --mount type=bind,source=/root/prometheus.yml,destination=/etc/prometheus/prometheus.yml --publish 9091:9090 --network net1 registry.cn-hangzhou.aliyuncs.com/zxh230/prometheus:v2.53.0
# 启动cadvisor
docker service create   --name cadvisor   --mode global   --publish 8080:8080   --mount type=bind,source=/,destination=/rootfs,readonly   --mount type=bind,source=/var/run,destination=/var/run,readonly   --mount type=bind,source=/sys,destination=/sys,readonly   --mount type=bind,source=/var/lib/docker,destination=/var/lib/docker,readonly   --mount type=bind,source=/dev/disk,destination=/dev/disk,readonly   --constraint 'node.platform.os == linux'   cadvisor:v0.47.0
# 启动node-export
docker service create --mode global --name node-exporter --network net1 --publish 9100:9100 registry.cn-hangzhou.aliyuncs.com/zxh230/node-exporter:v1.8.1
# 启动grafana
docker service create --name grafana --replicas 1 --publish mode=ingress,target=3000,published=3000 --network net1 -e "GF_SECURITY_ADMIN_PASSWORD=123.com" registry.cn-hangzhou.aliyuncs.com/zxh230/grafana:11.0.0
```

进入网页进行配置

------

创建网卡

docker01为nfs服务器
docker02配置tomcat容器与mysql容器

```shell
# 网段30.0.0.0，网关30.0.0.100
docker network create --driver bridge --subnet 30.0.0.0/24 --gateway 30.0.0.100 net2
# 安装nfs-server
yum -yq install nfs-utils
# 创建挂载点目录
mkdir /nfs
# 修改nfs配置文件
vim /etc/exports
###
/nfs *(rw,sync,no_root_squash)
###
# 创建mysql挂载点
mkdir -p /nfs/mysql
# 重启nfs
exportfs -r
systemctl restart nfs-server
# 查看可挂载点（docker01，03）
showmount -e 10.15.200.241
# 下载tomcat镜像
docker pull tomcat
# 进行配置
docker volume create --driver local --opt type=nfs --opt o=addr=10.15.200.241,rw --opt device=:/nfs aaa
docker run -itd --name tomcat -v aaa:/usr/local/tomcat/webapps/ROOT --network net2 -p 9090:8080 tomcat:latest 
docker exec -it tomcat bash
cd /usr/local/tomcat/
cp -r webapps.dist/* webapps/
exit
# 访问10.15.200.242:9090
```

![image-20240717095631888](https://gitee.com/zhaojiedong/img/raw/master/image-20240717095631888.png)

```shell
# 修改tomcat网页
cd /nfs
echo aaa > index.jsp
```

mysql构建 ——> [仙人指路](https://gitee.com/zhaojiedong/work/blob/master/%E7%AC%94%E8%AE%B0/7-22%E4%BD%9C%E4%B8%9A.md)
mysql自启动镜像 ——>  [仙人指路](https://gitee.com/zhaojiedong/work/blob/master/笔记/7_15实验报告.md)

```shell
# mysql持久化
mount -t nfs 10.15.200.241:/nfs /nfs
docker run -itd --mount type=bind,source=/nfs/mysql,target=/usr/local/mysql/data/ --name mysqldata 10.15.200.243:5000/mysql:8 bash
# 验证
cd /nfs
ls
ls /nfs/mysql/
```

![image-20240717044211539](C:/Users/zxh/AppData/Roaming/Typora/typora-user-images/image-20240717044211539.png)

------

 ### 第四题配置

nginx1.20  > [仙人指路](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/nginx-1.20.2.tar.gz)

php配置包 > [仙人指路](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/phpaaa.zip)

```shell
# 下载nginx:1.20镜像
docker pull nginx:1.20
# 批量配置nginx
mkdir nginx
cd nginx
vim Dockerfile
###
FROM registry.cn-hangzhou.aliyuncs.com/zxh230/rockylinux:9
RUN yum -y install iproute iputils procps-ng net-tools make gcc zlib-devel pcre-devel pcre zlib openssl openssl-devel
ADD nginx-1.20.2.tar.gz /
WORKDIR /nginx-1.20.2
RUN ./configure --prefix=/usr/local/nginx --sbin-path=/usr/sbin && make && make install
RUN /usr/sbin/nginx
WORKDIR /
EXPOSE 80/tcp
RUN echo zhaojiedong > /usr/local/nginx/html/index.html
CMD ["nginx","-g","daemon off;"]
###
docker build -t nginx:1.20 ./
cd ../
# 配置php镜像，将php包中解压出的文件移动到该目录下
mkdir php
cd php/
vim Dockerfile
###
FROM registry.cn-hangzhou.aliyuncs.com/zxh230/rockylinux:9
ADD php-8.2.7.tar.gz /
RUN yum -y install make vim iproute gcc openssl-devel zlib-devel pcre-devel sqlite-devel libxml2-devel bzip2-devel libcurl-devel freetype-devel
RUN cd /php-8.2.7/ && ./configure --prefix=/usr/local/php  --with-pdo-mysql  --with-openssl --with-freetype --with-jpeg --with-zlib --with-bz2 --enable-fpm --enable-sockets --enable-sysvshm --enable-mysqlnd --enable-xml --with-mysqli && make -j 6 && make install
RUN yes | cp -r /php-8.2.7/sapi/fpm/* /usr/local/php/etc/
RUN rm -rf /usr/local/php/etc/php-fpm.d/www.conf.default
COPY www.conf /usr/local/php/etc/php-fpm.d/
RUN mkdir -p /usr/local/nginx/html/
RUN mkdir /usr/local/nginx/html/ -p
CMD ["/bin/bash"]
###
docker build -t php:8 ./
# 启动web容器
docker run -itd --name web1 --network net2 --ip 30.0.0.10 -p 5555:80 nginx:1.20
docker run -itd --name web2 --network net2 --ip 30.0.0.20 -p 6666:80 nginx:1.20
# 分别进入两个web容器,更改nginx配置文件
docker exec -it web1 bash
docker exec -it web2 bash
vi /usr/local/nginx/conf/nginx.conf
# web1容器
location ~ \.php$ {
            root           html;
            fastcgi_pass   30.0.0.30:9000;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  /usr/local/nginx/html/index.php;
            include        fastcgi_params;
        }
# web2容器
location ~ \.php$ {
            root           html;
            fastcgi_pass   30.0.0.40:9000;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  /usr/local/nginx/html/index.php;
            include        fastcgi_params;
        }
# 更改后分别重载nginx
nginx -s reload
# 启动mysql容器
docker run -itd --name mysql --network net2 --restart always --ip 30.0.0.50 mysql:8 bash
# 授权
docker exec -it mysql mysql -uroot -p
create user 'root'@'30.0.0.%' identified by '123.com';
grant all on *.* to 'root'@'30.0.0.%';
exit
# 创建集群挂载镜像
mkdir /root/web   # 网页存放路径
docker create --name web --volume /root/web/:/usr/local/nginx/html/ busybox:1.36
# 启动php容器
docker run -itd --name php1 --volumes-from web --network net2 --ip 30.0.0.30 php:8
docker run -itd --name php2 --volumes-from web --network net2 --ip 30.0.0.40 php:8
# 更改php2配置文件
docker exec -it php2 bash
vi +41 /usr/local/php/etc/php-fpm.d/www.conf 
# 将listen =改为30.0.0.40:9000
# 查看php1的配置文件是否正确，php1监听30.0.0.30:9000,php2监听30.0.0.40:9000
# 启动php
docker exec -itd php1 /usr/local/php/sbin/php-fpm
docker exec -itd php2 /usr/local/php/sbin/php-fpm
# 创建网页文件
vim /root/web/index.php
###
<?php
session_start();
if (!isset($_SESSION['counter'])) {
    $_SESSION['counter'] = 0;
}

$_SESSION['counter']++;

if ($_SESSION['counter'] % 2 == 1) {
    try {
        $link = mysqli_connect('30.0.0.50','root','123.com');
        if($link) {
            echo "一, 数据库连接成功!!!\n";
        } else {
            echo "一, 数据库连接失败~~~\n";
        }
    } catch (mysqli_sql_exception $e) {
        echo "一, 数据库连接失败~~~\n";
    }
    phpinfo();
} else {
    try {
        $link = mysqli_connect('30.0.0.50','root','123.com');
        if($link) {
            echo "二, 数据库连接成功!!!\n";
        } else {
            echo "二, 数据库连接失败~~~\n";
        }
    } catch (mysqli_sql_exception $e) {
        echo "二, 数据库连接失败~~~\n";
    }
    phpinfo();
}
?>
###
# 验证访问是否轮询
http://10.15.200.242:5556
http://10.15.200.242:5555
# 多次访问实现轮询
```

