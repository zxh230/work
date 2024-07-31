有状态数据:比如:mysql 的存储，程序的 API 等等statefulset:
1 稳定的，唯一网络标识-不重复且由小到大，0起始期望值重新创建的 pod id 不变 ip 变化-由 DNS 实现:[pod-Name].[service-Name].[namespace]稳定的，持久的存储(volume 卷的时候讲)2有序的，优雅的部署和扩缩了3-扩展 由小到大 受到 minReadySeconds的影响-收缩 由大到小 /删除 时 不受 minReadySeconds 的影响4 有序的，自动的滚动更新rollingUpdate:由大到小更新patition 保护的副本，不受到滚动更新和回滚的影响patition 只能减少归零之后再增大，否则将有多个版本的副本

```shell
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 6
  minReadySeconds: 5
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
        - name: web
          containerPort: 80
# Service:---
# 定义了 Service 监听的端口是 80
# clusterIP: None：指定 Service 为 Headless 服务。Headless 服务不分配集群 IP，通常用于与 StatefulSet 配合使用时，以便每个 Pod 都可以被独立访问
# app: nginx：选择标签为 app: nginx 的 Pods，这些 Pods 将会接收发送到这个 Service的流量
# StatefulSet：---
# serviceName: "nginx"：指定与这个 StatefulSet 关联的 `ervice 名字为 nginx
# minReadySeconds: 5：指定 Pod 在被视为 Ready 状态之前，必须至少等待 5 秒
# ------
# Service：创建一个名为 nginx 的 Headless 服务，监听端口 80，并选择标签为 app: nginx 的 Pods
# StatefulSet：创建一个名为 web 的 StatefulSet，运行 6 个副本的 nginx 容器。每个 Pod 都会使用 nginx 服务进行网络标识
```