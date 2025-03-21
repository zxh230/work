要求：
1、redis部署在node1和node2上，当网络不通和无法ready时，容忍50s后被迁移。
2、mysql部署在node1和node3上，但是无法被系统驱离。

设备：
kube01	10.15.200.241
kube02	10.15.200.242
kube03	10.15.200.243

------

## redis

```shell
# 添加污点
kubectl taint node kube01 cpu=fast:NoExecute
kubectl taint node kube02 mem=big:NoExecute
kubectl taint node kube03 disk=ssd:NoExecute
# 查看污点
kubectl hello
```

 ![image-20240725012526902](https://gitee.com/zhaojiedong/img/raw/master/image-20240725012526902.png)

<a href="#hello">插件重构</a>

```shell
# 编写yaml文件
vim redis.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 2
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 6379
      tolerations:
      - key: "mem"
        operator: "Equal"
        value: "big"
        effect: "NoExecute"
        tolerationSeconds: 50
      - key: "cpu"
        operator: "Equal"
        value: "fast"
        effect: "NoExecute"
        tolerationSeconds: 50
      - key: "node.kubernetes.io/not-ready"
        operator: "Equal"
        effect: "NoExecute"
        tolerationSeconds: 50
      - key: "node.kubernetes.io/unreachable"
        operator: "Equal"
        effect: "NoExecute"
        tolerationSeconds: 50
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Equal"
        effect: "NoSchedule"
###
# 进行部署
kubectl apply -f redis.yaml
# 查看所在节点，infopod为今天所写的插件
kubectl infopod
```

 ![image-20240725000005138](https://gitee.com/zhaojiedong/img/raw/master/image-20240725000005138.png)

```shell
# 首先停止kube02的kubelet.service服务
systemctl stop kubelet.service
# 等待kube02的node节点状态变为noready
kubectl get nodes
# 查看驱离过程
kubectl infopod -w
***
# -w无法卡住终端时修改/usr/bin/kubectl-infopod插件
vim /usr/bin/kubectl-infopod
###
#!/bin/bash
kubectl get pod $1 -o custom-columns=NAME:.metadata.name,IP:.status.podIP,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
###
***
# 静静等待开始驱离
```

 ![image-20240725010853310](https://gitee.com/zhaojiedong/img/raw/master/image-20240725010853310.png)

==发现后续刷新的redis节点全部为kube01即可==

```shell
# 此时查看pod节点，因为kube02上已经停止了服务，导致主节点无法与其通信
# 使得原先的kube02上的redis pod还在
```

 ![image-20240725011330064](https://gitee.com/zhaojiedong/img/raw/master/image-20240725011330064.png)

```shell
## 图片大致解释
# 第一，三行为新开启的redis pod，属于正常运行状态
# 第四行的pod节点因为主节点无法连接kube02，所以无法驱离
# 第三行，为了维持redis的整体运行，主节点在运行上一步的驱离时会新增一个pod，但是无法连接到kube02
# 所以无法分配
```

==查看pod详细信息==

```shell
kubectl describe pods <任意redis pod节点>
# 看到驱离为50秒
```

![image-20240725012829471](https://gitee.com/zhaojiedong/img/raw/master/image-20240725012829471.png)

------

## mysql

```shell
# 编写mysql的yaml文件
vim mysql.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/hostname
                operator: In
                values:
                - kube01
                - kube03
      tolerations:
      - key: "cpu"
        operator: "Equal"
        value: "fast"
        effect: "NoExecute"
      - key: "disk"
        operator: "Equal"
        value: "ssd"
        effect: "NoExecute"
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Equal"
        effect: "NoSchedule"
      - key: node.kubernetes.io/disk-pressure
        operator: Exists
        effect: NoSchedule
      - key: node.kubernetes.io/memory-pressure
        operator: Exists
        effect: NoSchedule
      - key: node.kubernetes.io/network-unavailable
        operator: Exists
        effect: NoSchedule
      - key: node.kubernetes.io/not-ready
        operator: Exists
        effect: NoSchedule
      - key: node.kubernetes.io/pid-pressure
        operator: Exists
        effect: NoSchedule
      - key: node.kubernetes.io/unreachable
        operator: Exists
        effect: NoSchedule
      - key: node.kubernetes.io/unschedulable
        operator: Exists
        effect: NoSchedule
      containers:
      - name: mysql
        image: mysql:latest
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "123.com"
##
# 进行部署
kubectl apply -f mysql.yml
# 查看pod
kubectl infopod
```

 ![image-20240725012411621](https://gitee.com/zhaojiedong/img/raw/master/image-20240725012411621.png)

------

------

------

<h2><span name = "hello">编写插件</span></h2>

```shell
vim /usr/bin/kubectl-hello
### 将主机名kube1,2,3替换为自己的主机名
#!/bin/sh
echo "The message show all nodes taints:"
A=$(kubectl get node kube01 -o jsonpath='{range .spec.taints[*]}{"\t"}{.key}={.value}:{.effect}{"\n"}{end}')
B=$(kubectl get node kube02 -o jsonpath='{range .spec.taints[*]}{"\t"}{.key}={.value}:{.effect}{"\n"}{end}')
C=$(kubectl get node kube03 -o jsonpath='{range .spec.taints[*]}{"\t"}{.key}={.value}:{.effect}{"\n"}{end}')
echo -e "kube01:\n$A"
echo -e "kube02:\n$B"
echo -e "kube03:\n$C"
###
# 验证运行
kubectl hello
# 重构后的插件可以查看节点上所有的污点
```
 ![image-20240725013722441](https://gitee.com/zhaojiedong/img/raw/master/image-20240725013722441.png)