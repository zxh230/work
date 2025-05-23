要求：
使用 deployment 部署 pod，启动 DNS 服务，解析对应的域名。

解析https://www.k8shan.com完成以下内容：

1 访问域名 https://www.k8shan.com：显示：test good。

2 所有的 pod 均可以自动弹性伸缩

3 所有 pod 均不可被系统驱离

4 内存不得超过 100 Mi CPU 不得超过 500 豪核

> 实验步骤

```shell
# 生成证书密钥
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./k8s.key -out ./k8s.crt -subj "/CN=www.k8szxh.com"
# 导入证书
cp k8s.crt /etc/pki/ca-trust/source/anchors/
# 重新载入证书
update-ca-trust
# 创建证书密钥secret
kubectl create secret tls nginx-tls --key k8s.key --cert k8s.crt
# 创建网页
mkdir /html
echo "test good" > /html/index.html
# 使用已有的配置文件
cp /root/secret/{default,nginx}.conf ./
# 修改配置文件
vim default.conf
###
server {
    listen       443 ssl;
    server_name  www.k8szxh.com;
    ssl_certificate /etc/nginx/ssl/tls.crt;
    ssl_certificate_key /etc/nginx/ssl/tls.key;
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }
}
###
# 创建configmap
kubectl create configmap webconf --from-file default.conf 
# 编写部署文件
vim nginx.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 443
        resources:
          limits:
            cpu: 500m
            memory: 100Mi
          requests:
            cpu: 200m
            memory: 50Mi
        volumeMounts:
        - name: nginx-html
          mountPath: /usr/share/nginx/html/
        - name: web
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: default.conf
        - name: tls
          mountPath: /etc/nginx/ssl/
          readOnly: true
      tolerations:
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Equal"
        effect: "NoSchedule"
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
      volumes:
      - name: web
        configMap:
          name: webconf
      - name: tls
        secret:
          secretName: nginx-tls
      - name: nginx-html
        hostPath:
          path: /html
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
    - protocol: TCP
      port: 443
      targetPort: 443
###
# 编写ingress
vim ingress.yaml
###
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "https"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - www.k8szxh.com
    secretName: nginx-tls
  rules:
  - host: www.k8szxh.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port: 
              number: 443
###
# 编写hpa
vim hpa.yaml
###
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 120
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
###
# 开始部署
kubectl apply -f ./
# 写入域名解析
vim /etc/hosts
```
验证

访问 \https://www.k8szxh.com

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408051833687.png)

查看容器限制

`kubectl describe  deployments.apps web-deployment`

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408051834358.png)

验证是否扩缩
```shell
# 监控 pod 数量变化
watch -n 1 "kubectl get pods"
# 给予压力
kubectl exec -it web-deployment-6b9bf69d6b-k2qp4 -- dd if=/dev/zero of=/dev/null
# 只需等待
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408051839148.png)

> 时间最大的两个 pod 为最初的 pod，其余 pod 则是由于 cpu 压力过大，hpa 新开的 pod
> 停止给予 cpu 压力后，等待 2 分钟，看到 pod 数量缩减至 2 个

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408051844271.png)

查看 pod 是否无法被驱离

`kubectl describe pods web-deployment-6b9bf69d6b-tsvb2`

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408051845600.png)
