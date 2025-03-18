### labels 标签维度

*以数字或字母开头*

基于应用的横向维度（不同的pod有不同的标签）
基于版本的纵向维度（同一个pod有不同的版本）

lables：
[DomainName]  /  [key]  =  [value]

```shell
# 查看节点标签
kubectl get nodes 
# 查看pod标签
kubectl get pods --show-labels
```

![image-20240724135616408](https://gitee.com/zhaojiedong/img/raw/master/image-20240724135616408.png)

![image-20240724140416791](https://gitee.com/zhaojiedong/img/raw/master/image-20240724140416791.png)

pod-template-hash=8665b6f747

==yaml文件中 template 以下的文本的哈希值==

```shell
# 一个pod可以有多个标签
###
apiVersion: v1
kind: Pod
metadata:
  name: box
  labels:
    app: as
    rel: stable
spec:
  containers:
  - name: test1
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
###
kubectl get pods box --show-labels 
```

![image-20240724140826991](https://gitee.com/zhaojiedong/img/raw/master/image-20240724140826991.png) 

```shell
# 过滤标签
kubectl get pods -l app=as
```

 ![image-20240724140920951](https://gitee.com/zhaojiedong/img/raw/master/image-20240724140920951.png)

```shell
# 对标签所属的pod进行删除，可以一次性删除多个相同标签的pod
kubectl delete pods -l app=as
```

```shell
kubectl get pods  -l  app in '(mysql,nginx-php)'
kubectl get pods -L app
```

```shell
# 添加标签
kubectl label pods box env=test
```

 ![image-20240724141502740](https://gitee.com/zhaojiedong/img/raw/master/image-20240724141502740.png)

```shell
# 修改标签
kubectl label pods box env=test1 --overwrite 
# 删除一个标签
kubectl label pods box env-
```

![image-20240724141614554](https://gitee.com/zhaojiedong/img/raw/master/image-20240724141614554.png) 

------

![](https://gitee.com/zhaojiedong/img/raw/master/image-20240724142019498.png)

==有控制器预定义的标签不能进行更改==

```shell
# 将查询的内容以yaml格式进行输出
kubectl get pod box -o yaml
# 查询列参数
kubectl get pod -o custom-columns=NAME:.metadata.name,IP:.status.hostIP,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
# 写入脚本
vim kubectl-infopod
###
#!/bin/bash
kubectl get pod $1 -o custom-columns=NAME:.metadata.name,IP:.status.hostIP,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
###
# 移动后授予权限
cp kubectl-infopod /usr/bin/
chmod +x /usr/bin/kubectl-infopod
# 进行查询,可以自定义是否具体查询某个pod
kubectl-infopod box
kubectl-infopod
```

 ![image-20240724144712290](https://gitee.com/zhaojiedong/img/raw/master/image-20240724144712290.png)

```shell
# 将部署的pod调度到指定标签的节点
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-depolyment
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
      nodeSelector:
        dis: ssh		# 调度到dis标签为ssh的节点上
      containers:
      - name: nginx
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
###
# 为节点添加标签
kubectl label nodes kube02 dis=ssd
# 也可以修改文件使其强制部署在某个节点上
###
spec:
  nodeName: kube02
###
```

```shell
# 查看节点上的污点,hello为之前创建的插件
kubectl hello
```

 ![image-20240724151945751](https://gitee.com/zhaojiedong/img/raw/master/image-20240724151945751.png)

```shell
# 删除污点
kubectl taint node kube01 node-role.kubernetes.io/control-plane:NoSchedule-
```

operator:
Equal



```shell
- key: node.kubernetes.io/
operator: Exists
effect: NoExists
tolerationSeconds: 30   # 设置容忍时间
# 查看pod详细信息
kubectl describe --namespace kube-system pod kube-proxy-jdqlx
```

![837706db96e95e5c1f4d8ae03e35e24](https://gitee.com/zhaojiedong/img/raw/master/837706db96e95e5c1f4d8ae03e35e24.jpg)

```shell
# 数据驱离
kubectl taint node kube03 node-type=test:NoExecute
```
