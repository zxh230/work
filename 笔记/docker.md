#### docker

清空防火墙

```shell
iptables -F
iptables-save
systemctl stop firewalld
systemctl disable firewalld
getenforce 0
vim /etc/sysconfig/selinux
```

将enforcing更改为disabled

```shell
reboot         # 重启
setenforce 0   # 刷新
getenforce     # 验证
```

增加![image-20240703155239184](https://gitee.com/zhaojiedong/img/raw/master/image-20240703155239184.png)

增加三条内核参数

```shell
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
```

下载

```shell
# step 1: 安装必要的一些系统工具
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
# Step 2: 添加软件源信息
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
# Step 3
sudo sed -i 's+download.docker.com+mirrors.aliyun.com/docker-ce+' /etc/yum.repos.d/docker-ce.repo
# 安装docker
sudo yum -yq install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# 启动docker
systemctl start docker
docker -v # 查看版本
docker images # 查看镜像
# 配置镜像加速器
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://6kskcyjq.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
vim /etc/docker/daemon.json 
# 更改为
{
"registry-mirrors": [
        "https://docker.1panel.live.=",
        "https://docker.m.daoclude.io",
        "https://6kskcyjq.mirror.aliyuncs.com"]
}

# 重载
systemctl demon-reload
systemctl restart docker.service
docker info
# 下面的username为阿里云账户名，passwd为你的命名空间密码
sudo docker login --username=zjd230212 registry.cn-hangzhou.aliyuncs.com
# 拉取nginx1.20镜像
docker pull registry.cn-hangzhou.aliyuncs.com/zxh230/nginx:1.20
```



==*_如果修改了密码，则需要删除/etc/docker/daemon.json_*==



可信镜像仓库地址

[AtomHub 可信镜像仓库平台 · OpenAtom Foundation](https://atomhub.openatom.cn/)

*镜像名组成：*

| **Registry/DomainName**   | **Repository**                   | **Tag**      |
| ------------------------- | :------------------------------- | ------------ |
| 统一的docker registry地址 | Docker用来集中存放镜像文件的地方 | 镜像的版本号 |

打开AtomHub平台，搜索ubuntu

选择library/ubuntu

![image-20240703210306960](https://gitee.com/zhaojiedong/img/raw/master/image-20240703210306960.png)

复制镜像拉取命令并查看可用版本号

![image-20240703210546561](https://gitee.com/zhaojiedong/img/raw/master/image-20240703210546561.png)

拉取ubuntu：22.04的镜像

```shell
docker pull hub.atomgit.com/library/ubuntu:22.04
```

提示404错误，大概率网站服务器宕机

![image-20240703210922696](https://gitee.com/zhaojiedong/img/raw/master/image-20240703210922696.png)

前往另一个docker镜像网站并查看etcd的版本号

[etcd版本号列表](https://quay.io/repository/coreos/etcd?tab=tags&tag=v3.4.33)

拉取etcd:v3.4.33的版本

```shell
docker pull quay.io/coreos/etcd:v3.4.33
```



当指定拉取镜像的Registry/DomainName时，则拉取指定地址的镜像

而如果没有指定镜像地址，如：docker pull nginx:1.24

则会默认从docker Hub，也就是docker.io拉取镜像



```shell
# 查询ubuntu镜像，未指定最多显示25个
docker search ubuntu
# 查询前三个官方ubuntu镜像
docker search --filter is-official=true --limit 3 --no-trunc ubuntu
# 搜索对应镜像名的镜像
docker search quay.io/镜像名
# 当未指定拉取镜像的tag版本时，则默认拉取该镜像的latest版本
docker pull ubuntu
# 当查询一个镜像时，输出结果中第三列STARS为零，则表示没有该镜像
docker search quay.io/redis
```

![image-20240703212953173](https://gitee.com/zhaojiedong/img/raw/master/image-20240703212953173.png)



docker.fxxk.dedyn.io作为docker.io的镜像网站，可以用来查询镜像tag版本号

[网站入口](https://docker.fxxk.dedyn.io/)



如何删除镜像：

<left><a4>首先查询现有镜像</a4></left>

```
docker images
```

![image-20240703214210334](https://gitee.com/zhaojiedong/img/raw/master/image-20240703214210334.png)

```shell
# 第一种方式：指明镜像名称与tag版本
docker rmi quay.io/coreos/etcd:v3.4.33
# 第二章方式：指明镜像ID号
docker rmi cbcf23ccfc50
```

==给镜像重新标记==

```shell
docker tag ubuntu:latest aaa:latest  # 将默认版本的ubuntu重新标记为aaa
```

==重新标记后IMAGES ID和源镜像相同==

==此时不能通过指明镜像ID来进行删除镜像==

![image-20240703221940680](https://gitee.com/zhaojiedong/img/raw/master/image-20240703221940680.png)

下载镜像

```shell
docker save -o nginx:1.20  # 将镜像aaa:latest打包为nginx.tar文件
```

尝试将tar包文件加载为镜像

```
# 首先删除aaa:latest
docker rmi aaa:latest
# 然后进行载入
docker load --input nginx.tar
```

拉取镜像

```shell
docker pull grafana/grafana
docker pull prom/node-exporter
docker pull prom/prometheus
docker pull nginx:latest
docker pull nginx:1.20
# docker pull nginx:1.22
# docker pull registry.k8s.io/ingress-nginx/controller:v1.8.0
# docker pull kubernetesui/metrics-scraper:v1.0.8
# docker pull kubernetesui/dashboard:v2.7.0
# docker pull gcr.io/cadvisor/cadvisor:v0.47.0
# docker pull registry.k8s.io/metrics-server/metrics-server:v0.6.3
docker pull php:8-apache
# docker pull registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20230407
```

配置docker自启动并关闭防火墙

```shell
systemctl disable firewalld
systemctl enable docker
```

