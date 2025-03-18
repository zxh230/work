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

requests 和 limit 没有设置=BestEffort
requests 小于 limit=Burstable
requests 等于 limit=Guaranteed


```shell
apiVersion: v1
kind: ResourceQuota
metadata:
  name: cpu-and-mem
spec:
  hard:
    pods: 5
    services: 1
    services.loadbalancers: 2
# hard：这个字段定义了资源的硬性限制，即在这个命名空间中能够使用的资源上限。
# pods: 5：这个限制表示在这个命名空间中最多可以有 5 个 Pod。
# services: 1：这个限制表示在这个命名空间中最多可以创建 1 个 Service。
# services.loadbalancers: 2：这个限制表示在这个命名空间中最多可以创建 2 个带有 LoadBalancer 类型的 Service
```

```shell
apiVersion: v1
kind: ResourceQuota
metadata:
  name: cpu-and-mem
spec:
  scopes:
  - BestEffort
  - NotTerminatin
  hard:
    pods: 5
# scopes：这个字段定义了适用的资源范围。资源配额可以应用于不同的资源类别，这里指定了以下范围：
# BestEffort：表示这个资源配额适用于 `BestEffort` 类别的 Pod。`BestEffort` 是一种资源分配策略，用于不要求保证资源的 Pod。
# NotTerminatin：这是一个拼写错误，应该是 `NotTerminating`。这个范围表示这个资源配额适用于 NotTerminating 类别的资源，即不包括那些正在终止中的 Pod。
# pods: 5：指定了在命名空间中最多可以有 5 个 Pod 的限制
```