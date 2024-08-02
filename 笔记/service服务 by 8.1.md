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

```shell
spec:
  hostname: busybox-2
  setHostnameAsFQDN: true
# hostname: busybox-2 指定hostname主机名
# setHostnameAsFQDN: true 使得在pod内查询hostname时输出完整的FQDN主机名
spec:
  hostNetwork: true
  dnsPolicy: ClusterFirstWithHostNet
# dnsPolicy: ClusterFirstWithHostNet 可以使用节点上的dns进行解析
```
```shell
# 指定pod内的dns
spec:
  dnsPolicy: None
  dnsConfig:
    nameservers:
    - 114.114.114.114
    - 8.8.8.8
# 部署完成后进入pod查看
# 访问百度
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011826629.png)

~~~shell
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  sessionAffinity: ClientIP
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: nginx
# sessionAffinity: ClientIP 当设置essionAffinity: ClientIP时，来自同一客户端 IP 地址的所有请求都会被路由到同一个 Pod
~~~
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011838846.png)

可以访问nginx

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011839141.png)

修改cluster IP地址池范围

```shell
vim /etc/kubernetes/manifests/kube-apiserver.yaml 
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011845410.png)

```shell
# 重启
systemctl daemon-reload 
systemctl restart kubelet.service
# 修改文件
vim nginx-svc.yaml
###
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  clusterIP: 10.10.100.100
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: nginx
###
# 此时可以成功部署
```
当改为10.100.100.100时也可以成功部署

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011850339.png)

可以正常访问后端pod

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011851111.png)

指定后端节点IP
```shell
vim nginx-svc.yaml
###
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: nginx
  externalIPs:
  - 10.15.200.241
###
# 部署后查看
kubectl get svc -owide
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011854282.png)

进行访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011944169.png)


设置虚拟IP
```shell
vim nginx-svc.yaml
###
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: nginx
  externalIPs:
  - 10.15.200.241
  - 10.15.200.200
# 虚拟IP可以在物理机上进行访问，但是无法在浏览器上访问
```

```shell
# 在kube03上安装httpd，启动并生成网页文件
yum -yq install httpd
systemctl start httpd
echo "Im httpd from kube03" > /var/www/html/index.html
curl 10.15.200.243
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011949243.png)

```shell
vim ex-svc.yaml
###
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
---
apiVersion: v1
kind: Endpoints
metadata:
  name: my-service
subsets:
- addresses:
  - ip: 10.15.200.243
  ports: 
  - port: 80
###
# 部署后查看
kubectl get svc
kubectl describe svc my-service
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011954460.png)

访问service IP时可以代理到后端节点

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011955255.png)

同时，在容器中也能够进行访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408011956394.png)


使用主机名+service访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012137050.png)

```shell
vim nginx-svc.yaml
###
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  type: NodePort
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: nginx
###
# 查看
kubectl get svc
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012138910.png)

可以通过任意节点IP+端口访问后端pod

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012140997.png)

```shell
vim /etc/kubernetes/manifests/kube-apiserver.yaml 
# 增加之前删除service
- --service-node-port-range=40000-50000
# 重启
# 再次部署service，端口号范围变化
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012144589.png)

也可以指定端口号（同一范围）
```shell
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  type: NodePort
  ports:
  - protocol: TCP
    port: 8080
    nodePort: 40080
    targetPort: 80
  selector:
    app: nginx
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012146390.png)

验证仍然可以访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012147326.png)

开启ip_vs (三个节点全部开启)
```shell
modprobe -- ip_vs_sh
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
# 验证
lsmod |grep ip_vs
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012152049.png)

```shell
# 安装ipset,ipvsadm
yum -yq install ipset ipvsadm
# 修改配置
kubectl edit configmaps --namespace kube-system kube-proxy
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012155553.png)

```shell
# 查看
kubectl get daemonsets.apps -n kube-system 
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012158986.png)

重启kube-proxy
```shell
kubectl rollout restart daemonset -n kube-system kube-proxy 
```

查看轮询记录
```shell
ipvsadm -Ln
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012200348.png)

保存iptables中关于serviceIP地址的条目

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012201772.png)

轮询条目
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012203955.png)

查看pod IP地址是否与轮询地址对应

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012203956.png)

配置ingress
```shell
# 在kube02，kube03上创建网页文件
# kube02
mkdir -p /www/httpd
mkdir -p /www/nginx
echo "http by kube02" > /www/httpd/index.html
echo "nginx by kube02" > /www/nginx/index.html
# kube03
systemctl stop httpd
mkdir -p /www/httpd
mkdir -p /www/nginx
echo "http by kube03" > /www/httpd/index.html
echo "nginx by kube03" > /www/nginx/index.html
# 创建部署文件
vim nginx.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: nginx-cluster
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
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html/
      volumes:
      - name: www
        hostPath:
          path: /www/nginx/
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  selector:
    app: nginx
  ports:
  - name: http
    port: 80
    targetPort: 80
###
vim single.yaml
###
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: single-ingress
spec:
  ingressClassName: nginx
  defaultBackend:
    service:
      name: nginx
      port:
        number: 80
###
# 部署后查看
kubectl infopod 
kubectl get svc
kubectl get ingress
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012233351.png)

访问service IP地址，轮询访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012237963.png)


访问部署了 ingress 节点的IP地址，轮询访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408012237112.png)
******
多主机配置

新建service

```shell
vim httpd.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: httpd-cluster
spec:
  replicas: 3
  selector:
    matchLabels:
      app: httpd
  template:
    metadata:
      labels:
        app: httpd
    spec:
      containers:
      - name: httpd
        image: httpd:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        volumeMounts:
        - name: httpd
          mountPath: /usr/local/apache2/htdocs/
      volumes:
      - name: httpd
        hostPath:
          path: /www/httpd/
---
apiVersion: v1
kind: Service
metadata:
  name: httpd
spec:
  selector:
    app: httpd
  ports:
  - name: http
    port: 80
    targetPort: 80
###
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408020854604.png)


![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408020853870.png)


配置 ingress

```shell
vim domain.yaml
###
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: http-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: "nginx.zxh.com"
    http:
      paths:
      - pathType: Prefix
        path: /
        backend:
          service:
            name: nginx
            port:
              number: 80
  - host: "httpd.zxh.com"
    http:
      paths:
      - pathType: Prefix
        path: /
        backend:
          service:
            name: httpd
            port:
              number: 80
# 指向创建好的两个service
###
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408020856739.png)

修改域名解析文件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408020858670.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408020858978.png)

创建新的网页
```shell
mkdir /www/nginx/prod
mkdir /www/httpd/test
echo "httpd test" > /www/httpd/test/index.html
echo "nginx prod" > /www/nginx/prod/index.html
# 更改domain.yaml
cp domain.yaml url.yaml
vim url.yaml
###
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: http-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: "nginx.zxh.com"
    http:
      paths:
      - pathType: Prefix
        path: /prod
        backend:
          service:
            name: nginx
            port:
              number: 80
      paths:
      - pathType: Prefix
        path: /test
        backend:
          service:
            name: httpd
            port:
              number: 80
###
```
