### 7_11作业

### 要求：

> 1、构建一个rockylinux9.4版本的base镜像。 可以使用常规命令且可以使用ifconfig。 2、并且将上述镜像传到registry的镜像仓库，使用用户名good，密码123456

### 设备：

docker01 10.15.200.241

docker02 10.15.200.242

### 步骤：

1，创建rockylinux9.4镜像

使用supermin构建镜像，安装基础软件包

```bash
# 配置镜像内拥有的基本包
yum -yq install supermin
mkdir -p base7_11/images/rocky9
cd base7_11/images
supermin --prepare yum coreutils dnf iproute iputils net-tools bash wget curl tar rpm -o rocky9/
# 制作操作系统
mkdir systemd
supermin -v --build --format chroot rocky9/ -o systemd/
cp /etc/resolv.conf systemd/etc/
# 查看镜像内的yum仓库，发现有版本变量
cat systemd/etc/yum.repos.d/rocky.repo
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112001009.png)

```bash
# 创建件，写入版本号
echo 9.4 > systemd/etc/dnf/vars/releasever
# 挂载设备
chroot systemd/ bash
mknod -m 666 /dev/random c 1 8
mknod -m 666 /dev/unandom c 1 9
# 导入密钥
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9
exit
# 制作镜像
tar -cf rockylinux9_4.tar systemd/
# 创建空镜像
tar -cvf /dev/null |docker import - scratch
# 使用Dockerfile构建镜像
vim Dockerfile
### 
FROM scratsh
LABEL  maintainer="zxh"
ADD rockylinux9_4.tar /
CMD ["/bin/bash"]
###
docker build -t rockylinux:9.4 ./
docker images
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112043657.png)

配置私人仓库registary

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

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240816132403.png)


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
# 创建用户
docker run --entrypoint htpasswd httpd:2 -Bbn good 123456 > /root/base7_11/user/htpasswd
# 关闭其他容器
docker rm -f $(docker ps -qa)
# 启动镜像
docker run -itd -p 5000:5000 --restart always --volume /opt/data/registry/:/var/lib/registry --volume /root/base7_11/user/:/root/base7_11/user -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" -e REGISTRY_AUTH_HTPASSWD_PATH=/root/base7_11/user/htpasswd  --volume /root/base7_11/certs/:/root/base7_11/certs/  -e REGISTRY_HTTP_TLS_CERTIFICATE=/root/base7_11/certs/domain.cert -e REGISTRY_HTTP_TLS_KEY=/root/base7_11/certs/domain.key --name registry registry:2
```

在docker02上登录：

```bash
docker login 10.15.200.241:5000
# 用户名good
# 密码123456
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112114601.png)

```bash
# 下载镜像
docker pull 10.15.200.241:5000/rockylinux:9.4
# 验证
docker images
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407112115598.png)