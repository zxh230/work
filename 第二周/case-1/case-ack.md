![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904232638.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904232654.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904232706.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904233040.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904235111.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904235122.png)


将没通过的全部授权开通

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904233740.png)

等待初始化完成

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904234448.png)

进入集群详情页----> 通过云终端管理集群

创建一个 yaml 文件

```shell
vim nginx.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
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
          image: nginx:latest
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 80
###
# 部署
kubectl apply -f nginx.yaml
```