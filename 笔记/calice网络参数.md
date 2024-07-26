calice 网络参数
cidr：表示 IP 地址池的 CIDR 范围，表示从这个网段分配

ipipMode：
ip in/over-ip 隧道模式：外部是物理机的 ip 包头，内部是 calico 的 ip 包头，在这个模式下，每个 node 会有一个 tunl0 的设备
用于创建三层隧道
BGP mesh 模式：他在每个节点上都运行一个虚拟路由（BIRD）并通过 BGP 协议与所有的虚拟路由共享路由信息，缺点： 节点越多，连接数量线性增长

natOUtgoing：指字段启动出段流量的 NAT（从 Pod 发出的流量）地址转换
true 表示：calico 对 pod 发出的流量进行 NAT 转换，实现上网
disabled 表示：ture 表示禁用地址池，false 表示启用地址池
nodeSelector：哪些节点可以从这个 ip 地址池中获取 IP 地址

==ippool地址池yaml文件格式==

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: box
  labels:
    app: as
    rel: stable
  annotations:
    cni.projectcalico.org/ipv4pools: '["pool1"]'
spec:
  containers:
  - name: test1
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
```

```shell
# 部署
kubectl apply -f pool1.yaml
# 编写yaml
vim nginx.yaml
###
apiVersion: v1
kind: Pod
metadata:
  name: box
  labels:
    app: as
    rel: stable
  annotations:
    cni.projectcalico.org/ipv4pools: '["pool1"]'
spec:
  containers:
  - name: test1
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
###
# 部署
kubectl apply f nginx.yaml
# 查看IP地址
kubectl infopod
```

 ![image-20240726094558410](https://gitee.com/zhaojiedong/img/raw/master/image-20240726094558410.png)

```shell
# 查看已有地址池
calicoctl get ippools --allow-version-mismatch
```

