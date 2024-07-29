### Rs

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

