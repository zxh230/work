要求：

作业：
1、构建一个 rockylinux 9.4 版本的 base 镜像
   可以使用常规命令且可以使用 ifconfig
2 基于上述命令使用 Dockerfile 构建 mysql 镜像
  健康检查文件: 每隔三秒检查 ifconfig 是否存在
  正常运行该镜像, 并且创建数据库 gooddb, 创建后创建检查点
3 将上述镜像传到 registry 的镜像仓库，使用用户名 good，密码 123456，账户在第二台 docker 主机登录后，可以下载该镜像
4 在第二台 docker 主机上运行该镜像, 并且使用第一台 docker 的检查点开始运行

创建私人仓库
```shell
# docker01
yum -yq install openssl openssl-devel
sysctl -p
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819195327.png)

```shell
# 创建证书
mkdir -p /etc/docker/certs.d/10.15.200.241:5000/
mkdir /certs
openssl req -newkey rsa:4096 -nodes -sha256 -keyout /certs/domain.key -x509 -days 3650 -out /certs/domain.cert
# IP地址为仓库所在的IP地址
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819195443.png)

```shell
cp /certs/domain.cert /etc/docker/certs.d/10.15.200.241\:5000/
# 提前在docker02(10.15.200.242)上创建目录
scp /certs/domain.cert 10.15.200.242:/etc/docker/certs.d/10.15.200.241\:5000/ca.crt
# 创建用户
mkdir -p /user
# httpd镜像无版本要求，默认即可，用户名密码可以自定义
docker run --entrypoint htpasswd httpd:latest -Bbn zxh 123456 > /user/htpasswd
# 启动容器
docker run -itd -p 5000:5000 --restart always --volume /opt/data/registry/:/var/lib/registry --volume /user/:/user -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" -e REGISTRY_AUTH_HTPASSWD_PATH=/user/htpasswd  --volume /certs/:/certs/  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.cert -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key --name registry registry:2
# 登录仓库
docker login 10.15.200.241:5000
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819195833.png)

docker 02 (10.15.200.242) 登录

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819195947.png)

#### 构建 rocky 9 bese 镜像

```shell
mkdir rocky9
supermin --prepare yum coreutils dnf iproute iputils net-tools bash wget curl tar rpm -o rocky9/
# 确认软件包是否安装
cat rocky9/packages 
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819200848.png)

```shell
mkdir systemd
supermin -v --build --format chroot rocky9/ -o systemd/
echo 9.4 > systemd/etc/dnf/vars/releasever
# 进入系统
chroot systemd/ bash
##
mknod -m 666 /dev/random c 1 8
mknod -m 666 /dev/unandom c 1 9
# 查看验证是否添加并一致
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819201141.png)

```shell
# 导入rpm密钥
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9
exit
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
docker build -t rocky9:zxh ./
docker images
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819202036.png)

#### 构建 mysql 并配置健康检查

```shell

```