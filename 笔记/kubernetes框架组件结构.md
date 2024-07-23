## kubernetes框架/组件结构

![7305b3e5e7f63d1c1f763ef2d89cdf5](https://gitee.com/zhaojiedong/img/raw/master/7305b3e5e7f63d1c1f763ef2d89cdf5.jpg)控制面板：control-plane

子节点：work

主kube节点：

 ![image-20240723135013469](https://gitee.com/zhaojiedong/img/raw/master/image-20240723135013469.png)

容器网络配置：calico

查看docker01上的节点

```shell
kubectl get pod --namespace kube-system -o wide |grep docker01
```

 ![image-20240723135242338](https://gitee.com/zhaojiedong/img/raw/master/image-20240723135242338.png)

coredns

etcd：关系型数据库，存储集群中所有配置，执行get命令等

kube-proxy：数据转发结构

kube-scheduler：调度器，调度应用，

pod：k8s的最小调度单元

controller-manager：集群级别功能，处理执行部署方式，失败节点处理，跟踪pod运行

kubelet：采集当前主机内所有的节点数据信息并发送

crictl：充当agent，执行与容器相关的命令，例如创建容器

service：把信息转发到kube-proxy，*kube-proxy使用集群代理转发*

------

```shell
# 在集群中创建pod，其中运行镜像nginx，副本数量3个
kubectl create deployment test --image nginx:latest --replicas 3
# 查看集群中所有的pod
kubectl get pod
```

 ![image-20240723144407233](https://gitee.com/zhaojiedong/img/raw/master/image-20240723144407233.png)

```shell
# 查看计算机中包含的空间
kubectl get namespaces 
```

 ![image-20240723144618450](https://gitee.com/zhaojiedong/img/raw/master/image-20240723144618450.png)

```shell
# 查看容器日志
kubectl logs [pod节点名称]
# 删除临时pod节点
kubectl delete pod [节点名称]
# 删除pod
kubectl delete deployments.apps [pod名称]
# 关于删除原则：谁创建谁删除
# 创建临时pod使其维持活跃
kubectl run box1 --image busybox:1.36 -- sleep 1d
```

kuberbets 无法使用 bash 作为前台程序，依然遵循容器命令生命周期等于容器生命周期规则

```shell
# 登录容器
kubectl attach pods/box1
# ctrl+C退出时不会导致容器停止
# 在容器内执行命令
kubectl exec -it pods/box1 -- /bin/sh
```



kuberbets 插件：

```shell
# 创建kubectl插件
vim kubectl-hello
###
#!/bin/sh
echo "The message show all nodes taints:"
A=$(kubectl describe nodes docker01 |grep -i Taints |tr -s "")
B=$(kubectl describe nodes docker02 |grep -i Taints |tr -s "")
C=$(kubectl describe nodes docker03 |grep -i Taints |tr -s "")
echo "docker01:"$A
echo "docker02:"$B
echo "docker03:"$C
###
# 移动到/usr/bin下，授予执行权限
cp kubectl-hello /usr/bin/
chmod +x /usr/bin/kubectl-hello 
# 运行时直接输入插件名称
kubectl-hello
# 查看已有的插件
kubectl plugin list
```

------

k8s支持 json 和 yaml 格式

json：查看内容，例如:inspect

yaml：缩进（层级结构）必须相同，空格与TAB不能混用，严格区分大小写，并列关系加 - ，缩进关系表示包含

#### 编写yaml文件

```shell
# 实例：
apiversion: apps/v1   		# 支持的版本，可以使用kubectl api-versions查询当前支持的版本
kind: Deployment			# 
metadata: 					# 元数据
  name: nginx-deployment
spec: 						# 表示规范
  replicas: 3				# 副本数量3个
  							# 标签
# 查询文件格式写法，缩进使用.代替
kubectl explain deployment.spec.template.spec.containers.imagePullPolicy
# 例：部署nginx
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
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
###
# 生成一份模板
kubectl create deployment newhan --image httpd:latest -o yaml --dry-run=client > test.yaml
```

```shell
# 在pod内运行两个容器
apiVersion: v1
kind: pod
metafata:
  name: box
  namespace: prod
  labels:
    app: myapp
spec: 
  containers:
  - name: test1
    image: busybox:1.36
    imagePullPolicy: IfNotPresent
    command:
    - /bin/sh
    - -c
    - sleep 1d
  - name: test2
    image: busybox:1.36
    imagePullPolicy: IfNotPresent
    args: ["sleep","1d"]
# 运行命令有 command 和 arg s两种格式
# command 和 ENTYRYPOINT 相同，

```

