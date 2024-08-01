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
