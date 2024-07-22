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
cat <<EOF | sudo tee /etc/sysctl.conf
net.bridge.bridge-nf-call-iptables  = 1   
net.bridge.bridge-nf-call-ip6tables = 1    
net.ipv4.ip_forward                 = 1    
EOF
 # 网络桥接处理数据包调用ipv4进行过滤，保证桥接卡的数据包可以安装iptables规则处理
 # 网络桥接处理数据包调用ipv6进行过滤
 # 表示路由规则，打开主机的路由转发（不同网段通信）
# 验证
sudo sysctl --system
```

|![image-20240722142323316](https://gitee.com/zhaojiedong/img/raw/master/image-20240722142323316.png)

```shell
# 安装containerd.io
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's+download.docker.com+mirrors.aliyun.com/docker-ce+' /etc/yum.repos.d/docker-ce.repo
sudo yum makecache
yum -y install containerd.io
# 初始化
containerd config default | sudo tee /etc/containerd/config.toml 
```

![image-20240722145639034](https://gitee.com/zhaojiedong/img/raw/master/image-20240722145639034.png)

```shell
# 修改配置文件
vim /etc/containerd/config.toml 
###
sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.9"
SystemdCgroup = true
config_path = "/etc/containerd/certs.d"
###
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
# 修改文件
echo "vm.swappiness = 0" >> /etc/sysctl.d/k8s.conf 
# 注释掉fstab最后一行
vim /etc/fstab
```

 ![image-20240722173944058](https://gitee.com/zhaojiedong/img/raw/master/image-20240722173944058.png)

```shell
# 关闭swap分区
sudo swapoff -a
# 验证
free -m
# swap为0即可
```

 ![image-20240722174225521](https://gitee.com/zhaojiedong/img/raw/master/image-20240722174225521.png)

```shell
# 准备安装kubernetes
# 配置仓库
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/repodata/repomd.xml.key
EOF
# 安装
yum install -y kubelet-1.30.1 kubeadm-1.30.1 kubectl-1.30.1
# 使其可以tab
echo "source <(kubeadm completion bash)" >> ~/.bashrc
echo "source <(nerdctl completion bash)" >> ~/.bashrc
echo "source <(kubectl completion bash)" >> ~/.bashrc
echo "source <(crictl completion bash)" >> ~/.bashrc
# 刷新
source ~/.bashrc
# 
crictl config runtime-endpoint unix:///run/containerd/containerd.sock
# 更改
vim /etc/crictl.yaml
```

 ![image-20240722180244127](https://gitee.com/zhaojiedong/img/raw/master/image-20240722180244127.png)

```shell
# 检查时间同步，没有域名解析可以用ip
for h in docker0{1..3}
do
ssh $h -q "date"
done
# 添加阿里云时间服务器
vim /etc/chrony.conf
# 添加
server ntp1.aliyun.com iburst
server ntp2.aliyun.com iburst
# 重启
systemctl restart chronyd.service 
```

  ![image-20240722182036569](https://gitee.com/zhaojiedong/img/raw/master/image-20240722182036569.png)

```shell
# 开始同步时间
chronyc sources -n
```

 ![image-20240722182156178](https://gitee.com/zhaojiedong/img/raw/master/image-20240722182156178.png)

```shell
# 生成配置文件，只在主节点，显示乱码为初始化错误
kubeadm config print init-defaults > init.yaml
vim init.yaml
```

 ![image-20240722182857213](https://gitee.com/zhaojiedong/img/raw/master/image-20240722182857213.png)

```shell
# 开机自启
systemctl enable kubelet.service 
# 初始化集群
kubeadm init --config=init.yaml
# 
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=/etc/kubernetes/admin.conf
# 更改dns
vim /etc/NetworkManager/system-connections/ens160.nmconnection 
# 更改为谷歌的公共dns：8.8.8.8
# 重启
systemctl restart NetworkManager.service 
# 尝试下载
curl https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml -O
# 更改文件
vim calico.yaml 
# 注意缩进！！！
```

 ![image-20240722184742461](https://gitee.com/zhaojiedong/img/raw/master/image-20240722184742461.png)

```shell
# 开始配置
kubectl apply -f calico.yaml
```

```shell
# 客户端加入（docker02,docker03）命令位置在之前的输出信息中
```

 ![image-20240722185232603](https://gitee.com/zhaojiedong/img/raw/master/image-20240722185232603.png)

```shell
# 查看节点信息
kubectl get nodes
# 查看是否running
kubectl get pod --namespace kube-system
# 开始下载
kubectl get pod --namespace kube-system -w
# 等待全部running
```

 ![image-20240722192404189](https://gitee.com/zhaojiedong/img/raw/master/image-20240722192404189.png)

```shell
# 自启动
systemctl enable containerd.service 
# 如果长时间（5~10分钟）没有running完成，尝试删除改节点重试
 kubectl delete pod [节点名称]  -n kube-system
```

 ![image-20240722192149134](https://gitee.com/zhaojiedong/img/raw/master/image-20240722192149134.png)

```shell
# 更改消息日志不更新(三台服务器)
vim /etc/rsyslog.d/01-blocklist.conf
###
if $msg contains "run-containerd-runc-k8s" and $msg contains "mount: Deactivated successfully" then {
 stop
}
###
# 重启
systemctl daemon-reload 
systemctl restart rsyslog.service
# 查看日志是否更新（等待5~10秒不更新即可）
tail -f /var/log/messages 
```



```shell
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
cadvisor:v0.49.2
metrics-server:v0.7.1
kube-webhook-certgen:v1.4.1
controller:v1.10.1
grafana：10.0.9
node-exporter：v1.81
prometheus：2.53.0
alermanager：0.27.0 
```

kubuadm reset