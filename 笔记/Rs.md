### Rs

```shell
 1 # 声明api的版本。
 2 apiVersion: v1
 3 # kind代表资源的类型，资源是ReplicationController。
 4 kind: ReplicationController
 5 # 资源叫什么名字，是在其属性metadata里面的。
 6 metadata:
 7   # 第一个属性name的值是myweb，即ReplicationController的名字就叫做myweb。
 8   name: myweb
 9 # spec是详细，详细里面定义了一个容器。
10 spec:
11   # 声明副本数量是2，代表了RC会启动两个相同的Pod。
12   replicas: 2
13   # 选择器。
14   selector:
15     app: myweb
16   # Pod的启动模板，和Pod的yaml配置信息基本差不多的，几乎一样，但是这里没有名称，是因为两个Pod名称不能完全一样的。
17   # 没有指定名称，RC会随机生成一个名称。
18   template:
19     # 资源叫什么名字，是在其属性metadata里面的。但是这里让RC随机生成指定数量的名称。
20     metadata:
21       # 给Pod贴上了一个标签，标签是app: web，标签是有一定的作用的。
22       labels:
23         app: myweb
24     # spec是详细，详细里面定义了一个容器。
25     spec:
26       # 定义一个容器，可以声明多个容器的。
27       containers:
28         # 容器的名称叫做myweb
29         - name: myweb
30         # 使用了什么镜像，可以使用官方公有的，也可以使用私有的。
31           image: 192.168.110.133:5000/nginx:1.13
32         # ports定义容器的端口。
33           ports:
34         # 容器的端口是80，如果容器有多个端口，可以在后面接着写一行即可。
35             - containerPort: 80
```

```shell
apiVersion: v1
kind: ReplicationController
metadata:
  name: rc-rest
spec:
  replicas: 3
  selector: 
    app: rcpod
  template: 
    metadata: 
      labels: 
        app: rcpod
    spec:
      containers:
      - name: rctest
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
```

```shell
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-rest
  labels:
    app: guestbook
    tier: frontend
spec:
  replicas: 3
  selector: 
    matchLabels:
      app: rspod
  template: 
    metadata: 
      labels: 
        app: rspod
    spec:
      containers:
      - name: rctest
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
```

```shell
apiVersion: v1
kind: Pod
metadata:
  name: box1
  labels:
    app: rspod
spec:
  containers:
  - name: test1
    image: nginx:1.24
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
---
apiVersion: v1
kind: Pod
metadata:
  name: box2
  labels:
    app: rspod
spec:
  containers:
  - name: test1
    image: nginx:1.24
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
# 部署
kubectl apply -f pod.yaml 
# 查看事件
kubectl get events | grep box1
kubectl get events | grep box2
```

![image-20240729094919145](https://gitee.com/zhaojiedong/img/raw/master/image-20240729094919145.png)

```shell
# 将副本数下调为1个
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-rest
  labels:
    app: guestbook
    tier: frontend
spec:
  replicas: 1
  selector: 
    matchLabels:
      app: rspod
  template: 
    metadata: 
      labels: 
        app: rspod
    spec:
      containers:
      - name: rctest
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
# 部署pod后再部署rs
# 发现pod数量被删除为1个
```

```shell
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-rest
  labels:
    app: guestbook
    tier: frontend
spec:
  replicas: 5
  selector:
    matchExpressions:
    - {key: tier, operator: In, values: [frontend,canary]}
    - {key: app, operator: In, values: [guestbook, test]}
  template:
    metadata:
      labels:
        app: test
        tier: canary
    spec:
      containers:
      - name: rstest
        image: httpd:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
# 部署后修改标签
# 如果修改的标签值为多标签中的值则不会发生变化
# 反之则会新增一个pod，并且改变的pod不再受其控制
```

```shell
# --cascade=orphan  删除pod时不会删除已经创建的pod
kubectl delete -f rs.yaml --cascade=orphan
# 查看该pod相关配置
 kubectl get pods rs-rest-b8fx5 -o yaml
```

 ![image-20240729101609940](https://gitee.com/zhaojiedong/img/raw/master/image-20240729101609940.png)

```shell
# 重新绑定控制器时，只需要有一个标签即可
```

```shell
# 查看滚动更新的版本的信息
kubectl rollout history deployment we --revision 1
# 回滚到上一个版本
kubectl rollout undo deployment we 
# 回滚到指定版本
kubectl rollout undo deployment we --to-revision 1
# 
kubectl set image deployment/we nginx=nginx:latest --recursive=true
# 更新容器镜像
kubectl patch deployments.apps we --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/image","value":"nginx:zxh"}]'
```

```shell
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: we
  annotations:
    kubernets.io/change-cause: "Image update to nginx:1.22"
spec:
  strategy:
    rollingUpdate:
      maxSurge: 35%
      maxUnavailable: 35%
    type: Recreate
  revisionHistoryLimit: 10
  replicas: 10
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.24
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
```


滚动更新失败的原因：
Quota 不足
Readiness Probe 失败
image pull 失败 ^a59729
