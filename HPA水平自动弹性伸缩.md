Metrics server：收集 kubelet 的指标并公开
供给 pod 自动水平扩缩(HPA)和自动垂直扩缩(VPA)
可以使用 kubectl top 命令查看指标信息
仅用于自动扩缩为目的，监控软件自行安装其他采集 agent
tips：
适用于集群单一部署
每 15s 采集一次数据
占用 cpu 1毫核和 2MB 内存
[Metrics-server github官网](https://github.com/kubernetes-sigs/metrics-server)