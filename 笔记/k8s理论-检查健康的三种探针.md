1. pod 必须健康
2. container 健康
3. 容器内的service健康：systemctl status 
4. 服务文件健康：cat/ls
三种探针类型：
exec探针：通过执行指定的命令来检查容器的健康状态。如果命令的退出码是 0，则探针成功，否则探针失败。
http Get探针：通过发送 HTTP GET 请求到容器的指定路径和端口来检查容器的健康状态。如果响应的状态码是 200-399 之间，则探针成功，否则探针失败
tcpSocket探针：通过尝试连接容器的指定端口来检查容器的健康状态。如果可以建立连接，则探针成功，否则探针失败
##### exec 探针：
```shell
# 
apiVersion: v1
kind: Pod
metadata:
  name: readiness
spec:
  containers:
  - name: readiness
    image: busybox:1.36
    imagePullPolicy: IfNotPresent
    args:
    - /bin/sh
    - -c
    - touch /tmp/test; sleep 10; rm -fr /tmp; sleep 1d
    readinessProbe:
      exec:
        command:
        - cat
        - /tmp/test
      initialDelaySeconds: 10
      periodSeconds: 5
# readinessProbe：定义探针
# exec：使用命令执行探针
# conmmand：定义使用的命令
# initialDelaySeconds：在容器启动后，等待 10 秒钟再开始执行就绪探针
# periodSeconds: 每隔 5 秒钟定期执行一次就绪探针，检查容器状态
```
##### httpGet探针：
```shell
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: we
  annotations:
    kubernets.io/change-cause: "Image update to nginx:1.22"
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
        readinessProbe:
		  httpGet:
            path: /
            port: 80
          periodSeconds: 1
# readinessProbe: 定义了一个就绪探针，用于判断容器是否已经准备好接受流量
# httpGet: 使用 HTTP GET 请求探针。这个探针会向容器内的一个 HTTP 端点发送 GET 请求，并根据响应状态码来判断容器是否准备就绪
# path: 请求的路径,/表示请求根路径
# port: 目标端口
# periodSeconds: 每隔 1 秒钟执行一次就绪探针
```
##### tcpSocket探针：
```shell
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: we
  annotations:
    kubernets.io/change-cause: "Image update to nginx:1.22"
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
        readinessProbe:
          tcpSocket:
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 1
# tcpSocket 探针尝试连接指定端口来检查容器的健康状态
```

```shell
apiVersion: v1
kind: Pod
metadata:
  name: liveness
spec:
  containers:
  - name: liveness
    image: busybox:1.36
    imagePullPolicy: IfNotPresent
    args:
    - /bin/sh
    - -c
    - touch /tmp/test; sleep 30; rm -fr /tmp/test; sleep 1d
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/test
      initialDelaySeconds: 10
      periodSeconds: 5
```

```shell
apiVersion: v1
kind: Pod
metadata:
  name: liveness
spec:
  containers:
  - name: liveness
    image: busybox:1.36
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
    readinessProbe:
      exec:
        command:
        - cat
        - /usr/share/nginx/html/index.html
      initialDelaySeconds: 15
      periodSeconds: 1
    args:
    - /bin/sh
    - -c
    - touch /tmp/test; sleep 30; rm -fr /tmp/test; sleep 1d
    livenessProbe:
      tcpSocket:
        port: 80
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 5
    startupProbe:
      httpGet:
        path: /
        port: 80
      failureThreshold: 30
      periodSeconds: 10
# livenessProbe用于确定容器是否仍在运行,如果探针失败，Kubernetes 会重启容器
# timeoutSeconds: 5 探针的超时时间。如果在 5 秒钟内没有收到响应，探针会认为检查失败
```

```shell
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: we
  annotations:
    kubernets.io/change-cause: "Image update to nginx:1.22"
spec:
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
      - name: box
        image: busybox:1.36
        imagePullPolicy: IfNotPresent
        args:
        - /bin/sh
        - -c
        - sleep 10; touch /tmp/test; sleep 1d
        readinessProbe:
          exec:
            command:
            - cat
            - /tmp/test
          initialDelaySeconds: 10
          periodSeconds: 5
```
滚动更新失败的原因[[k8s理论-Rs#^a59729]]
