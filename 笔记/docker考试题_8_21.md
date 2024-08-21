配置私人仓库
```shell
# docker02
yum -yq install openssl openssl-devel
sysctl -p
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819195327.png)

```shell
# 创建证书
mkdir -p /etc/docker/certs.d/10.15.200.242:5000/
mkdir /certs
openssl req -newkey rsa:4096 -nodes -sha256 -keyout /certs/domain.key -x509 -days 3650 -out /certs/domain.cert
# IP地址为仓库所在的IP地址
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240821174756.png)


```shell
cp /certs/domain.cert /etc/docker/certs.d/10.15.200.242\:5000/
# 提前在docker01(10.15.200.241)上创建目录
scp /certs/domain.cert 10.15.200.241:/etc/docker/certs.d/10.15.200.242\:5000/ca.crt
# 创建用户
mkdir -p /user	
# httpd镜像无版本要求，默认即可，用户名密码可以自定义
docker run --entrypoint htpasswd httpd:latest -Bbn zxh 123456 > /user/htpasswd
# 编写compose文件启动registry
vim docker-compose.yaml
### 挂载路径与变量路径需要与之前创建时一一对应
services:
registry:
  container_name: registry
  image: registry:2
  ports:
  - 5000:5000
  restart: always
  volumes:
  - /opt/data/registry/:/var/lib/registry
  - /user/:/user
  - /certs/:/certs/
  environment:
    REGISTRY_AUTH: htpasswd
    REGISTRY_AUTH_HTPASSWD_REALM: Registry Realm
    REGISTRY_AUTH_HTPASSWD_PATH: /user/htpasswd
    REGISTRY_HTTP_TLS_CERTIFICATE: /certs/domain.cert
    REGISTRY_HTTP_TLS_KEY: /certs/domain.key
###
# 启动registry
docker compose up -d
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240821175027.png)

```shell
# 测试登录
docker login 10.15.200.242:5000
# 测试上传与下载
docker tag registry:2 10.15.200.242:5000/registry:2
docker push 10.15.200.242:5000/registry:2 
# docker01上登录并下载
docker login 10.15.200.242:5000
docker pull 10.15.200.242:5000/registry:2
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240821175149.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240821175204.png)

docker 01 上登录并下载：

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240821175237.png)

******
第三题

```shell
# 创建配置文件
vim nginx1.conf
###

###
```




******
第四题

配置 zabbix 监控

```shell
# docker01
```