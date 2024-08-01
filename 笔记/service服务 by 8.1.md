当任意pod被部署时，在其内的容器的`/etc/resolv.conf`会写入新的dns
内容为`kube-system`空间中的service IP地址
![[Pasted image 20240801165525.png]]

```shell
# nginx.yaml 文件内容
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: web
spec:
  replicas: 3
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
查看 `kube-dns` 的详细信息发现其内的pod IP指向两个IP地址

该IP地址指向 kube-system 空间内的两个pod

![[Pasted image 20240801165439.png]]

在 pod 中通过挂载实现 dns 解析
```shell
# 查看 pod 运行在那个节点上
kubectl infopod 
# 去对应节点查看正在运行的容器
crictl ps
# 查看相应容器的信息
crictl inspect <pod ID>
```
![[Pasted image 20240801165610.png]]
```shell
# 查看挂载内容
cat <挂载路径>
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011703471.png)
******
```shell
# 创建命名空间
kubectl create namespace test
# 部署 test.yaml 文件
apiVersion: apps/v1
kind: Deployment
metadata:
  name: newhan
  namespace: test
spec:
  replicas: 3
  selector:
    matchLabels:
      app: newhan
  strategy: {}
  template:
    metadata:
      labels:
        app: newhan
    spec:
      containers:
      - image: httpd:latest
        name: httpd
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: ns-svc
  namespace: test
spec:
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: newhan
    # 验证
    kubectl get pod -n test
    kubectl get service -n test
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011717104.png)
```shell
# 启动容器
kubectl run box --rm -it --image rockylinux:9 --image-pull-policy IfNotPresent -- /bin/bash
# 查看dns
cat /etc/resolv.conf
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011722207.png)
```shell
# 下载软件包
dnf -y install bind-utils
# 解析名称
nslookup ns-svc.test
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011724536.png)
```shell
# 容器内访问test空间中的httpd pod
curl ns-svc.test:8080
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011725521.png)
```shell
vim domainame.yaml 
###
apiVersion: v1
kind: Service
metadata:
  name: default-subdomain
spec:
  selector:
    name: busybox
  clusterIP: None
  ports:
  - name: foo
    port: 1234
    targetPort: 1234
---
apiVersion: v1
kind: Pod
metadata:
  name: box1
  labels:
    name: busybox
spec:
  hostname: busybox-1
  containers:
  - name: test1
    image: rockylinux:9
    imagePullPolicy: IfNotPresent
    command:
    - sleep
    - 1d
---
apiVersion: v1
kind: Pod
metadata:
  name: box2
  labels:
    name: busybox
spec:
  hostname: busybox-2
  containers:
  - name: test2
    image: rockylinux:9
    imagePullPolicy: IfNotPresent
    command:
    - sleep
    - 1d
###
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011750039.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011750563.png)

```shell
kubectl exec -it box1 -- bash
dnf install -yq bind-utils
nslookup 
# 进行解析
cat /etc/resolv.conf
nslookup default-subdomain
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011752022.png)

此时无法解析主机名

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011754362.png)

