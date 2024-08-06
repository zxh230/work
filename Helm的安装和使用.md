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
# 
```

