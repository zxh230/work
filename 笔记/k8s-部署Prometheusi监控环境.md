### 要求：
1. 使用初始化容器创建 https 的证书和密钥, 使用 deployment 部署 nginx:latest 副本 3 个, 并且启动 https 的访问.
2. 使用 poststart, 创建 index.html 页面内容为: poststart good.
3. 使用 daemonset 部署 cadvisor 和 node-exporter 在所有的节点, 且不可被驱离.
4. 使用 deployment 部署 Prometheus 服务端 和 grafana 副本各 1 个
5. 在 node1 上.访问 grafana 页面可以查看容器和主机状态
------
- 生成ssl密钥，挂载到创建nginx容器，使其支持https访问
- 使用 poststart, 创建 index.html 页面内容为: poststart good
```shell
# 创建作业目录
vim https/
cd https/
# 创建alpine.yaml文件
vim alpine.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-https
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
      initContainers:
      - name: init-ssl
        image: alpine:latest
        command: ["/bin/sh", "-c"]
        args:
          - |
            apk add --no-cache openssl &&
            mkdir -p /etc/nginx/ssl &&
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
              -keyout /etc/nginx/ssl/tls.key \
              -out /etc/nginx/ssl/tls.crt \
              -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/CN=mydomain.com";
        volumeMounts:
        - name: ssl-volume
          mountPath: /etc/nginx/ssl
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 443
        volumeMounts:
        - name: ssl-volume
          mountPath: /etc/nginx/ssl
        lifecycle:
          postStart:
            exec:
              command: ["/bin/sh", "-c", "echo 'poststart good' > /usr/share/nginx/html/index.html"]
        command: ["/bin/sh", "-c"]
        args:
          - |
            echo 'server {
                listen 443 ssl;
                server_name mydomain.com;
                ssl_certificate /etc/nginx/ssl/tls.crt;
                ssl_certificate_key /etc/nginx/ssl/tls.key;
                location / {
                    root   /usr/share/nginx/html;
                    index  index.html index.htm;
                }
                ssl_protocols       TLSv1.2 TLSv1.3;
                ssl_ciphers         HIGH:!aNULL:!MD5;
            }' > /etc/nginx/conf.d/default.conf && \
            nginx -g 'daemon off;'
      volumes:
      - name: ssl-volume
        emptyDir: {}
###
# 注解***
# initContainers用于定义初始化任务
# alpine:latest可以更换为任意可安装 openssl 软件包的系统镜像
# 安装 openssl 软件包，生成一对密钥文件
# args:
#        - |
#           apk add --no-cache openssl &&
#           mkdir -p /etc/nginx/ssl &&
#           openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
#             -keyout /etc/nginx/ssl/tls.key \
#             -out /etc/nginx/ssl/tls.crt \
#             -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/CN=mydomain.com";
# 创建共享卷
# volumeMounts:
#       - name: ssl-volume
#         mountPath: /etc/nginx/ssl
# 之后为创建nginx pod，修改配置文件使其支持https并监听443端口，挂载共享卷共享ssl密钥
# ***
# 部署
kubectl apply -f alpine.yaml
# 验证访问
curl -k https://10.10.138.61
```
验证访问结果
![](https://gitee.com/zhaojiedong/img/raw/master/202407301621943.png)
查看挂载卷 `kubectl describe pods nginx-https-545fc557f7-9gllb`
![](https://gitee.com/zhaojiedong/img/raw/master/202407301622297.png)
- - - - - -
- 使用 daemonset 部署 cadvisor 和 node-exporter 在所有的节点, 且不可被驱离
```shell
# 拉取镜像
nerdctl pull registry.cn-hangzhou.aliyuncs.com/zxh230/node-exporter:v1.8.1 --namespace k8s.io
# 更改标签，不更改时下面yaml文件中需要更改镜像名，改名则三台都需要改
nerdctl --namespace k8s.io tag registry.cn-hangzhou.aliyuncs.com/zxh230/node-exporter:v1.8.1 node-exporter:v1.8.1
# 创建cadvisor.yaml
vim cadvisor.yaml
###
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  labels:
    app: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Equal
          effect: NoSchedule
        - key: node.kubernetes.io/disk-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/memory-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/network-unavailable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/not-ready
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/pid-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unreachable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unschedulable
          operator: Exists
          effect: NoSchedule
      hostPID: true
      containers:
      - name: node-exporter
        image: node-exporter:v1.8.1
        args:
        - --path.procfs=/host/proc
        - --path.sysfs=/host/sys
        - --collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)
        ports:
        - containerPort: 9100
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: cadvisor
spec:
  selector:
    matchLabels:
      name: cadvisor
  template:
    metadata:
      labels:
        name: cadvisor
    spec:
      hostNetwork: true
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Equal
          effect: NoSchedule
        - key: node.kubernetes.io/disk-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/memory-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/network-unavailable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/not-ready
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/pid-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unreachable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unschedulable
          operator: Exists
          effect: NoSchedule
      containers:
        - name: cadvisor
          image: cadvisor:v0.49.1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          volumeMounts:
            - name: rootfs
              mountPath: /rootfs
              readOnly: true
            - name: sys
              mountPath: /sys
              readOnly: true
            - name: containerd
              mountPath: /var/lib/containerd/
              readOnly: true
            - name: disk
              mountPath: /dev/disk
              readOnly: true
      volumes:
        - name: rootfs
          hostPath:
            path: /
        - name: sys
          hostPath:
            path: /sys
        - name: containerd
          hostPath:
            path: /var/lib/containerd/
        - name: disk
          hostPath:
            path: /dev/disk
###
# 部署
kubectl apply -f cadvisor.yaml
# 查看pod节点，是否一个节点一个pod
kubectl get pods -o wide
```
![](https://gitee.com/zhaojiedong/img/raw/master/202407301708645.png)
浏览器验证，分别访问 8080 以及 9100 端口
![](https://gitee.com/zhaojiedong/img/raw/master/202407301710644.png)

![](https://gitee.com/zhaojiedong/img/raw/master/202407301713332.png)
将kube02,kube03关机，验证是否无法被驱离
![](https://gitee.com/zhaojiedong/img/raw/master/202407301728456.png)
节点未发生变化，证明无法被驱离
******
- 在 node1 上使用 deployment 部署 Prometheus 服务端 和 grafana 副本各 1 个
```shell
# 拉取镜像
nerdctl --namespace k8s.io pull registry.cn-hangzhou.aliyuncs.com/zxh230/grafana:11.0.0
nerdctl --namespace k8s.io pull registry.cn-hangzhou.aliyuncs.com/zxh230/prometheus:v2.53.0
# 更改标签，不更改时下面yaml文件中需要更改镜像名
nerdctl --namespace k8s.io tag registry.cn-hangzhou.aliyuncs.com/zxh230/prometheus:v2.53.0 prometheus:v2.53.0
nerdctl --namespace k8s.io tag registry.cn-hangzhou.aliyuncs.com/zxh230/grafana:11.0.0 grafana:11.0.0
# 创建kan.yaml文件，更改主机名与IP地址
vim kan.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      hostNetwork: true
      securityContext:
        fsGroup: 65534
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Equal
          effect: NoSchedule
        - key: node.kubernetes.io/disk-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/memory-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/network-unavailable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/not-ready
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/pid-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unreachable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unschedulable
          operator: Exists
          effect: NoSchedule
      nodeSelector:
        kubernetes.io/hostname: kube01
      initContainers:
        - name: init-config
          image: busybox
          command: ["/bin/sh", "-c"]
          args:
            - |
              echo "global:
                scrape_interval:     15s
                evaluation_interval: 15s
                external_labels:
                  monitor: 'codelab-monitor'
              rule_files:
                - 'prometheus.rules.yml'
              scrape_configs:
                - job_name: 'prometheus'
                  static_configs:
                    - targets: ['10.15.200.241:9091','10.15.200.241:8080','10.15.200.241:9100','10.15.200.243:9100','10.15.200.243:8080','10.15.200.242:9100','10.15.200.242:8080']" > /etc/prometheus/prometheus.yml
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
      containers:
        - name: prometheus
          image: prom/prometheus:v2.53.0
          args:
            - "--config.file=/etc/prometheus/prometheus.yml"
            - "--storage.tsdb.path=/prometheus"
            - "--web.listen-address=:9091"
            - "--web.enable-lifecycle"
            - "--storage.tsdb.no-lockfile"
          ports:
            - containerPort: 9091
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
            - name: storage
              mountPath: /prometheus
      volumes:
        - name: config
          emptyDir: {}
        - name: storage
          emptyDir:
            sizeLimit: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  labels:
    app: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      hostNetwork: true
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Equal
          effect: NoSchedule
        - key: node.kubernetes.io/disk-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/memory-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/network-unavailable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/not-ready
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/pid-pressure
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unreachable
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/unschedulable
          operator: Exists
          effect: NoSchedule
      nodeSelector:
        kubernetes.io/hostname: kube01
      containers:
        - name: grafana
          image: grafana:11.0.0
          ports:
            - containerPort: 3000
          env:
            - name: GF_SECURITY_ADMIN_PASSWORD
              value: "123.com"
###
# 部署
kubectl apply -f kan.yaml
# 查看pod部署情况
kubectl get pods
```
![](https://gitee.com/zhaojiedong/img/raw/master/202407302000156.png)

浏览器验证
访问Prometheus（端口号9091）
![](https://gitee.com/zhaojiedong/img/raw/master/202407302000313.png)
访问Grafana（端口号3000）
![](https://gitee.com/zhaojiedong/img/raw/master/202407302003996.png)
创建监控图表，模板编号选择（16522  待定）
![](https://gitee.com/zhaojiedong/img/raw/master/202407302005853.png)
