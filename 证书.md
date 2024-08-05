生成证书密钥
```shell
# 创建证书密钥
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=www.zxh.com"
# 创建secret
kubectl create secret tls nginx-test-tls --key tls.key --cert tls.crt 
# 复制nginx配置文件
kubectl run web --image nginx:latest --image-pull-policy IfNotPresent
kubectl exec -it web -- cat /etc/nginx/nginx.conf > nginx.conf
kubectl exec -it web -- cat /etc/nginx/conf.d/default.conf > default.conf
# 修改配置文件
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408050901394.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408050901784.png)

