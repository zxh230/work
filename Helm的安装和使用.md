安装 Helm

[下载Heml](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/helm-v3.15.3-linux-amd64.tar.gz)
```shell
# 配置heml命令包
tar -xf helm-v3.15.3-linux-amd64.tar.gz
cd linux-amd64
chmod +x heml
mv heml /usr/local/sbin/
# 使其可以tab
echo "source <(helm completion bash)" >> ~/.bashrc
source ~/.bashrc
# 添加仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
# 查看helm仓库
helm repo list
# 
```

helm 的三大概念：

chart：代表 helm 的包，可以看作：dnf，apt，brew，

repostory：用来存放和共享 charts 的地方，可以看作为：仓库地址

release：是 kubernetes 中 chart 的实例

helm 安装 charts 到 kubernetes 中，每次安装都会创建一个新的 release，可以在 helm 的 chart repository 中寻找到新的 chart

