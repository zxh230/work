要求：

四台 ECS 云服务器

三台组成 k 8 s 环境

一台 docker 环境

******
部署 k 8 s (server 1，server 2，server 3)
```shell
# svr1,svr2,svr3
iptables -F
iptables-sav
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
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's+download.docker.com+mirrors.aliyun.com/docker-ce+' /etc/yum.repos.d/docker-ce.repo
yum -y install containerd.io
containerd config default | sudo tee /etc/containerd/config.toml 
# 修改配置文件
vim /etc/containerd/config.toml 
###
sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.9"
SystemdCgroup = true
config_path = "/etc/containerd/certs.d"
###
```
![image-20240722160050972](https://gitee.com/zhaojiedong/img/raw/master/image-20240722160050972.png)
![image-20240722160022913](https://gitee.com/zhaojiedong/img/raw/master/image-20240722160022913.png)
![image-20240722155931246](https://gitee.com/zhaojiedong/img/raw/master/image-20240722155931246.png)
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
wget https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/nerdctl-1.7.6-linux-amd64.tar.gz
tar -xf nerdctl-1.7.6-linux-amd64.tar.gz 
mv nerdctl /usr/local/bin/
chmod +x /usr/local/bin/nerdctl
echo "source <(nerdctl completion bash)" >> ~/.bashrc
source ~/.bashrc
systemctl daemon-reload
systemctl restart containerd.service
echo "vm.swappiness = 0" >> /etc/sysctl.conf
sudo swapoff -a
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/repodata/repomd.xml.key
EOF
yum install -y kubelet-1.30.1 kubeadm-1.30.1 kubectl-1.30.1
echo "source <(kubeadm completion bash)" >> ~/.bashrc
echo "source <(nerdctl completion bash)" >> ~/.bashrc
echo "source <(kubectl completion bash)" >> ~/.bashrc
echo "source <(crictl completion bash)" >> ~/.bashrc
source ~/.bashrc
crictl config runtime-endpoint unix:///run/containerd/containerd.sock
vim /etc/crictl.yaml
```
![image-20240722180244127](https://gitee.com/zhaojiedong/img/raw/master/image-20240722180244127.png)
```shell
# 以下操作只在主节点进行！
kubeadm config print init-defaults > init.yaml
vim init.yaml
# 蓝色框代表无需更改，但需要与之后的对应
```
![image-20240724151145548](https://gitee.com/zhaojiedong/img/raw/master/image-20240724151145548.png)
```shell
systemctl enable kubelet.service
kubeadm init --config=init.yaml
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=/etc/kubernetes/admin.conf
vim /etc/NetworkManager/system-connections/ens160.nmconnection 
curl https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml -O
vim calico.yaml
# 与上面的网段所对应
```
![image-20240724151238403](https://gitee.com/zhaojiedong/img/raw/master/image-20240724151238403.png)
```shell
# 自行写入三台机器的域名解析
# 需要三台都写入
vim /etc/hosts
```
```shell
# 开始配置
kubectl apply -f calico.yaml
```
![image-20240722185232603](https://gitee.com/zhaojiedong/img/raw/master/image-20240722185232603.png)

**==从节点加入集群，加入之前需写入三台机器的域名解析==**

```shell
# 更改消息日志不更新(三台服务器)
vim  <<EOF | tee /etc/rsyslog.d/01-blocklist.conf
###
if $msg contains "run-containerd-runc-k8s" and $msg contains "mount: Deactivated successfully" then {
 stop
}
EOF
###
# 重启
systemctl daemon-reload 
systemctl restart rsyslog.service
```
```shell
# 查看节点信息
kubectl get po -n kube-system
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240906091225.png)

******
部署 devops

