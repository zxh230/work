要求：
service的端口号为：9090。
使用ingress金丝雀发布：当“头部消息”有vip:user，显示：[name]。否则显示“hansir”
使用ingress实现：1、访问域名[name].com，跳转到https://www.[name].com
2、访问域名https://www.[name].com/canary/new：显示：hansir
3、访问域名https://www.[name].com/stable/old：显示：[name]
其中，[name] 将替换为 `zxh` ,如有需要可自行替换

> 开始编写

```shell
# 作业目录
mkdir jsq
cd jsq/
# 创建证书与密钥
mkdir certs/
cd certs/
openssl req -newkey rsa:4096 -nodes -sha256 -keyout ./a.key -x509 -days 3650 -out ./a.cert -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/CN=mydomain.com";
# 创建secret
kubectl create secret generic zxh-tls --from-file=tls.crt=./a.crt --from-file=tls.key=./a.key --type=kubernetes.io/tls
# 查看secret
kubectl get secret zxh-tls -o yaml
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021824622.png)

```shell
# 编写new.yaml
vim new.yaml
###

###
```

******
生成密钥
```shell
# 域名可以更改
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./tls.key -out ./tls.crt -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/CN=www.zxh.com"
# 创建secret
kubectl create secret generic zxh-tls --from-file=tls.crt=./tls.crt --from-file=tls.key=./tls.key --type=kubernetes.io/tls
# 验证
kubectl get secrets zxh-tls -o yaml
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408031215997.png)

```shell
# 在kube02,kube03上创建网页目录与文件
mkdir -p /nginx/canary/new
mkdir -p /nginx/stable/old
echo zxh > /nginx/stable/old/index.html
echo hansir > /nginx/canary/new/index.html
# 编写nginx.yaml
vim nginx.yaml
###
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate /etc/nginx/ssl/tls.crt;
        ssl_certificate_key /etc/nginx/ssl/tls.key;
        ssl_verify_client off;

        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
---
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
        - containerPort: 443
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/ssl.conf
          subPath: nginx.conf
        - name: zxh-tls
          mountPath: /etc/nginx/ssl
          readOnly: true
        - name: nginx-web
          mountPath: /usr/share/nginx/html
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
      - name: zxh-tls
        secret:
          secretName: zxh-tls
      - name: nginx-web
        hostPath:
          path: /nginx
          type: Directory
###
# 部署后验证
curl -k --key tls.key https://10.108.41.42/canary/new/
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408031250515.png)

```shell

```