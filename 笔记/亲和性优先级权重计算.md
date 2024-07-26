### 亲和性优先级/权重计算

企业的 nodelables
[城市] – [区域] – [机房] – [机架] – [PC-X]

企业的 pod lables
[]  – []

#### 强制亲和

```shell
spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: gpu
                operator: In
                values:
                - "true"
```

#### 相对亲和

```shell
    spec:
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 80
            preference:
              matchExpressions:
              - key: zone
                operator: In  
                values:
                - beijing  
          - weight: 70
            preference:  
              matchExpressions:
              - key: zone  
                operator: In  
                values:  
                - shanghai  
          - weight: 20
            preference:  
              matchExpressions:
              - key: local  
                operator: In
                values:
                - fengtai
```

preferred 相对亲和的 pod 部署数量计算：
server02：zone = bejing 80  local = fengtai 20
server04：zone = bejing 80  local = daxing 0
server03：zone = shanghai 70 local = xujiahui 0
server05：zone = shanghai 70 local = jingan 0

sever03 和 server02 的 pod 数量占比：70+0/80+40 = 35%
结果
如果将 pod 副本数量调整为 10，则 server2：6 个 pod，server3：4 个 pod
SelectorSpreadPriority：同一个 pod 调度策略中为了安全，确保不会把所有的 pod 调度到同一个 pod 上

------

```shell
# 运行镜像
kubectl run backend -l app=backend --image busybox:1.36 --image-pull-policy IfNotPresent -- sleep 1d
# 亲和

```

------

### calico 网络

IP 地址由 32 个 2 进制位数构成，每 8 个二进制用 .  断开
IP 地址被分为：网络位和主机位，分割的方法是子网掩码
子网掩码中 1 对应的数是网络位，0 对应的是主机位
正规的算法是：ip 与 subnet = 网段

calico 的工作原理总结：
calico 是一个纯三层的虚拟网络解决方案。(二层用 vxlan 通道)
calico 为每个容器分配一个 IP，每个 node 都是一个 router
简单说：每个 node 是一个独立网段

IP in ip ： ip 层封装 ip 层
外层封装：node 源/目的 ip
内层封装：pod（calico 网络的）源/目的 ip

Felix 运行在每个节点的 agent 进程
复制：网络接口 路由 arp 管理 acl 管理信息上报
etcd：与 k8s 使用相同的 etcd
复制：存储网络元数据，路由一致性(收敛状态)

BIRD 是一种软路由(软件的路由器)calico之间的网段转发，
ip forward 物理机间的网段 可以转发到宿主机的 ip从而实现联网
		启动是:BGP 路由协议--Route Reflector
Tips: 如果节点属于不同的二层网络,需要使用 IPinIP/Vxlan 做隧道

------

```shell
# 更改默认IP地址池
kubectl edit ippools.crd.projectcalico.org default-ipv4-ippool
# 查看是否生效
kubectl describe ippools.crd.projectcalico.org default-ipv4-ippool
```

![image-20240725165126605](https://gitee.com/zhaojiedong/img/raw/master/image-20240725165126605.png)

------

[calicoctl](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/calicoctl-linux-amd64 "点击下载")

```shell
# 配置calicoctl
mv calicoctl-linux-amd64 /usr/local/sbin/calicoctl
chmod +x /usr/local/sbin/calicoctl
```

