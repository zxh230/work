### kuberetes框架/组件结构

### 时间同步

```shell
# 清空防火墙
iptables -F
iptables-save
# 关闭防火墙，diable防火墙
systemctl stop firewalld
systemctl disable firewalld
# 关闭selinux
vim /etc/sysconfig/selinux
reboot
# 进行初始化
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
##--
sudo modprobe overlay
sudo modprobe br_netfilter
##--
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1    # 网络桥接处理数据包调用ipv4进行过滤，保证桥接卡的数据包可以安装iptables规则处理
net.bridge.bridge-nf-call-ip6tables = 1    # 网络桥接处理数据包调用ipv6进行过滤
net.ipv4.ip_forward                 = 1    # 表示路由规则，打开主机的路由转发（不同网段通信）
EOF
# 验证
sudo sysctl --system
```

|![image-20240722142323316](https://gitee.com/zhaojiedong/img/raw/master/image-20240722142323316.png)

```shell
# 安装containerd.io
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's+download.docker.com+mirrors.aliyun.com/docker-ce+' /etc/yum.repos.d/docker-ce.repo
sudo yum makecache fast
yum -y install containerd.io
# 初始化
containerd config default | sudo tee /etc/containerd/config.toml 
```

![image-20240722145639034](https://gitee.com/zhaojiedong/img/raw/master/image-20240722145639034.png)

```shell
# 修改配置文件
sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.9"
SystemdCgroup = true
config_path = "/etc/containerd/certs.d"
```

|![image-20240722160050972](https://gitee.com/zhaojiedong/img/raw/master/image-20240722160050972.png)

|![image-20240722160022913](https://gitee.com/zhaojiedong/img/raw/master/image-20240722160022913.png)

|![image-20240722155931246](https://gitee.com/zhaojiedong/img/raw/master/image-20240722155931246.png)

```shell
# 创建镜像索引
mkdir -p /etc/containerd/certs.d/docker.io
vim /etc/containerd/certs.d/docker.io/hosts.toml
###
server = "https://docker.io"

[host."https://docker.1panel.live"]
  capabilities = ["pull","resolve"]
  skip_verify = true
[host."https://docker.m.daocloud.io"]
  capabilities = ["pull","resolve"]
  skip_verify = true
[host."https://6kskcyjq.mirror.aliyuncs.com"]
  capabilities = ["pull","resolve"]
  skip_verify = true
###
# 下载nerdctl-1.7.6-linux-amd64.tar.gz
# https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/nerdctl-1.7.6-linux-amd64.tar.gz
# 下载好后解压
tar -xf nerdctl-1.7.6-linux-amd64.tar.gz 
mv nerdctl /usr/local/bin/
chmod +x /usr/local/bin/nerdctl
# 使其能够tab
echo "source <(nerdctl completion bash)" >> ~/.bashrc
# 刷新
source ~/.bashrc
# 重启
systemctl daemon-reload
systemctl restart containerd.service
# 验证下载
nerdctl pull busybox:1.36
```

|![image-20240722160344693](https://gitee.com/zhaojiedong/img/raw/master/image-20240722160344693.png)

```shell
# 查看uuid
cat /sys/class/dmi/id/product_uuid
```

|![image-20240722160440196](https://gitee.com/zhaojiedong/img/raw/master/image-20240722160440196.png)

```shell
# 安装kubernetes

```

