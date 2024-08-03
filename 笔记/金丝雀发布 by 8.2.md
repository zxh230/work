要求：
service的端口号为：9090。
使用ingress金丝雀发布：当“头部消息”有vip:user，显示：[name]。否则显示“hansir”
使用ingress实现：1、访问域名[name].com，跳转到https://www.[name].com
2、访问域名https://www.[name].com/canary/new：显示：hansir
3、访问域名https://www.[name].com/stable/old：显示：[name]
其中，[name] 将替换为 `zxh` ,如有需要可自行替换

> 开始编写

生成密钥
```shell
# 域名可以更改
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./tls.key -out ./tls.crt -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/CN=www.zxh.com"
# 创建secret
kubectl create secret generic zxh-tls --from-file=tls.crt=./tls.crt --from-file=tls.key=./tls.key --type=kubernetes.io/tls
# 在kube02,kube03上创建网页目录与文件
mkdir -p /nginx/canary/new
mkdir -p /nginx/stable/old
echo zxh > /nginx/stable/old/index.html
echo hansir > /nginx/canary/new/index.html
```
编写部署文件：
```shell
# 编写nginx.yaml,内含Deployment以及service的部署
vim nginx.yaml
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
      - name: nginx-container
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: nginx.conf
        - name: nginx-web
          mountPath: /usr/share/nginx/html
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
      - name: nginx-web
        hostPath:
          path: /nginx
          type: Directory
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
# 编写conf.yaml,内含nginx配置文件
vim conf.yaml
###
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;

        location /canary/new {
            root /usr/share/nginx/html;
            index index.html;
        }

        location /stable/old {
            root /usr/share/nginx/html;
            index index.html;
        }

        location / {
            if ($http_vip = "user") {
                return 301 /stable/old;
            }
            return 301 /canary/new;
        }
    }
###
# 编写ingress.yaml,内含ingress策略
vim ingress.yaml
###
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - www.zxh.com
    secretName: zxh-tls
  rules:
  - host: www.zxh.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port: 
              number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingresa
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - zxh.com
    secretName: zxh-tls
  rules:
  - host: zxh.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port: 
              number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rewrite-zxh
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/rewrite-target: www.zxh.com
spec:
  ingressClassName: rewrite-nginx
  rules:
  - host: "zxh.com"
    http:
      paths:
      - pathType: Prefix
        path: /
        backend:
          service:
            name: nginx
            port:
              number: 80
###
```

部署顺序：

```shell
kubectl apply -f conf.yaml
kubeclt apply -f nginx.yaml
kubectl apply -f ingress.yaml
```

部署后验证：
```shell
# curl 访问
curl https://www.zxh.com/canary/new/
curl https://www.zxh.com/stable/old/
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408031747653.png)
