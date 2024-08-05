Metrics server：收集 kubelet 的指标并公开
供给 pod 自动水平扩缩(HPA)和自动垂直扩缩(VPA)
可以使用 kubectl top 命令查看指标信息
仅用于自动扩缩为目的，监控软件自行安装其他采集 agent
tips：
适用于集群单一部署
每 15s 采集一次数据
占用 cpu 1毫核和 2MB 内存
[Metrics-server github官网](https://github.com/kubernetes-sigs/metrics-server)
******
安装Metrics-server
```shell
# 获取安装文档
wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
# 拉取镜像
nerdctl --namespace k8s.io pull registry.cn-hangzhou.aliyuncs.com/zxh230/metrics-server:v0.7.1
# 修改文件
vim components.yaml
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408051104666.png)

```shell
# 部署
kubectl apply -f components.yaml
# 查看状态
kubectl get pods -n kube-system
# 等待15s后变为Running
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408051105049.png)

******
# 资源限制与QOS

