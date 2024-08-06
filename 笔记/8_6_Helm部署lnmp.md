要求：
写 yaml 文件 deployment 部署 nginx 副本 3 个.
写 yaml 文件 statefulset 部署 php 副本 3 个.
写 yaml 文件 statefulset 部署 mysql 副本 1 个.
写 yaml 文件以上每个部署一个 service.
写 yaml 文件 ingress 代理 https 协议的证书和密钥.
写 yaml 文件将证书和密钥作为 secret 存储
写 yaml 文件创建 nginx 的相关配置文件, php 的相关配置文件, mysql 的相关配置文件, 作为 configmap.
要求: 
1 将上述文件作为 helm 文件.
2 在 node 2 构建 helm 的私有 repository 仓库.
3 使用私有仓库文件内的 repo 安装以上全部文件.
结果:
访问 https://www.han.com/ 可以看到内容为: php 的测试页面及 mysql 连接测试.
>实验步骤

部署顺序 mysql-conf > mysql > php-conf> html > php > tls > nginx-conf > nginx

共 8 个 yaml 文件
```shell
# mysql.conf
vim mysql-conf.yaml
### 无改动
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-conf
data:
  my.cnf: |
    [mysqld]
    host-cache-size=0
    skip-name-resolve
    datadir=/var/lib/mysql
    socket=/var/run/mysqld/mysqld.sock
    secure-file-priv=/var/lib/mysql-files
    user=mysql
    pid-file=/var/run/mysqld/mysqld.pid
    [client]
    socket=/var/run/mysqld/mysqld.sock
    !includedir /etc/mysql/conf.d/
###
# mysql.yaml
vim mysql.yaml
### 可以不改
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "123.com"
        - name: MYSQL_DATABASE
          value: "zxh"
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-conf
          mountPath: /etc/my.cnf
          subPath: my.cnf
      volumes:
      - name: mysql-conf
        configMap:
          name: mysql-conf
---
apiVersion: v1
kind: Service
metadata:
  name: mysqlsvc
spec:
  type: ClusterIP
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
###
# php-conf.yaml
vim php-conf.yaml
### 无改动
apiVersion: v1
kind: ConfigMap
metadata:
  name: php-conf
data:
  www.conf: |
    ; Unix user/group of processes
    user = www-data
    group = www-data

    ; The address on which to accept FastCGI requests
    listen = 0.0.0.0:9000

    ; Set the process manager
    pm = dynamic

    ; The number of child processes to be created when pm is set to static and the maximum number of
    ; child processes to be created when pm is set to dynamic or ondemand.
    pm.max_children = 5

    ; The number of child processes created on startup.
    pm.start_servers = 2

    ; The minimum number of idle processes.
    pm.min_spare_servers = 1

    ; The maximum number of idle processes.
    pm.max_spare_servers = 3
###
# html.yaml
vim html.yaml
### 无改动
apiVersion: v1
kind: ConfigMap
metadata:
  name: html-php
data:
  index.php: |
    <?php
    error_reporting(E_ALL);
    ini_set('display_errors', 1);

    $db_host = getenv('DB_HOST');
    $db_port = getenv('DB_PORT') ?: '3306';  // 使用环境变量或默认值
    $db_name = 'zxh';
    $db_user = 'root';
    $db_pass = '123.com';

    echo "Attempting to connect to: $db_host:$db_port<br>";

    try {
        $dsn = "mysql:host=$db_host;port=$db_port;dbname=$db_name";
        $options = array(
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_TIMEOUT => 5, // 设置连接超时
        );
        $dbh = new PDO($dsn, $db_user, $db_pass, $options);
        echo '非常开心，数据库连接成功！！！<br>';
    } catch (PDOException $e) {
        echo '恭喜恭喜，数据库连接失败~~~<br>';
        echo '错误信息： ' . $e->getMessage() . '<br>';
        echo '错误代码： ' . $e->getCode() . '<br>';
    }

    echo "<br>Loaded PHP extensions:<br>";
    print_r(get_loaded_extensions());

    echo "<br><br>Environment variables:<br>";
    print_r($_ENV);

    phpinfo();
    ?>
###
# php.yaml
vim php.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-pod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: php
  template:
    metadata:
      labels:
        app: php
    spec:
      containers:
      - name: php
        image: php:8.1-fpm
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9000
        env:
        - name: DB_HOST
          value: "mysqlsvc"
        - name: DB_PORT
          value: "3306"
        command: ["/bin/sh"]
        args:
        - "-c"
        - |
          docker-php-ext-install mysqli pdo pdo_mysql && \
          mkdir -p /usr/share/nginx/html && \
          php-fpm
        volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html/
        - name: conf
          mountPath: /usr/local/etc/php-fpm.d/www.conf
          subPath: www.conf
      volumes:
      - name: html
        configMap:
          name: html-php
      - name: conf
        configMap:
          name: php-conf
---
apiVersion: v1
kind: Service
metadata:
  name: phpsvc
spec:
  type: ClusterIP
  clusterIP: 10.100.0.1
  selector:
    app: php
  ports:
    - port: 9000
      targetPort: 9000
###
# nginx-conf.yaml
vim nginx-conf.yaml
### 域名与证书对应
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-conf
data:
  aaa.conf: |
    server {
      listen 443 ssl;
      server_name www.zxh.com;
      root /usr/share/nginx/html;
      index index.php index.html index.htm;
      ssl_certificate /etc/nginx/ssl/tls.crt;
      ssl_certificate_key /etc/nginx/ssl/tls.key;

      location ~ \.php$ {
        fastcgi_pass 10.100.0.1:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
      }
    }
###
# tls.yaml
vim tls.yaml
### 更改为自己的密钥的base64编码格式 如（base64 ./k8s.crt）
apiVersion: v1
kind: Secret
metadata:
  name: nginx-tls
data:
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUREVENDQWZXZ0F3SUJBZ0lVQXo4eW5lV1FQdzN0SU5PMWlTblYvN244WVRzd0RRWUpLb1pJaHZjTkFRRUwKQlFBd0ZqRVVNQklHQTFVRUF3d0xkM2QzTG5wNGFDNWpiMjB3SGhjTk1qUXdPREEyTVRFeU5qQTVXaGNOTWpVdwpPREEyTVRFeU5qQTVXakFXTVJRd0VnWURWUVFEREF0M2QzY3VlbmhvTG1OdmJUQ0NBU0l3RFFZSktvWklodmNOCkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFJZnU3c0tTK3dZdUxsRnV0bG9MZ1p3bVNtWEcxeUVJWGRPU2dEYjgKMVQrcmUvL0o5V0N6akhEUytFSUZZUFNPRlUrdnlsU1ZZWm9YMnMzaDZFU0NpQ2hUdmpYc2thWTR2YmNvcjJOZgp6TkJXZ3VZbWlzdnhFYkFPa2VQU1N1VjNGYlY0RUpWT2U5d2JTTWRYdG1uVTBFei9tUlpHRVgrTlUyQUtzUGUwCnhSclJwUUZ2R20rTVk3cmkwQmxwU2MrekZvK29pYjVENEhtS2FFS2x6Ui96M09zWTZiUGg2bER4T3dWVUEvWHAKeHIvU0V3WGJiNkxYRFFPeThlSk84RkRCdHY4RU1OWmF0U0NYREQ2OFpDMk5CV3EvUUJxemgvQXFFMEQ0c2pjaQo0ZTNJTncvd01vYkNjZHFSUnBFNDdTVFpFZi9mSmRWRG94OGwyS2piRVFic3pyMENBd0VBQWFOVE1GRXdIUVlEClZSME9CQllFRlBUeFdyYU14ODZMK0R6NTYrVFY2N2JOUExMZE1COEdBMVVkSXdRWU1CYUFGUFR4V3JhTXg4NkwKK0R6NTYrVFY2N2JOUExMZE1BOEdBMVVkRXdFQi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dFQgpBQklZZTRuSmx2S1dzWmFYUTQ5SzJaZUEyMUZ0amxvM1pVOEdTU0Mwell1WFJKQ3ZuWXlUckZudGxOWHVML085CktzcTd0TXVkTEtLbCtFT3AyWDFKZ2trUm1FNVVoK1BxMjIwQnBEdDNzbTJENFUwVlp1dmkzR2x3V1BtcXBYSUYKQ1dpVDRvM2tkVzNnMnpJcmZQS2M2TmNxRDB5aVAwRU1nejJVMTYvcEtJdklNa1VmNjgrWEZXRFp3eWlIcHNiawpzM2tCUmxsb2ljdVBiVVFhRVFkZmVTUlNOdWJqdlMzVUVhVzB5L3ZBMndpOVBxUFUxbXMxL2dGSW1uMElMcTlxCk51NUxET3dOSkR1TmdScElKUzBsMUpTako5eU1wSFVTZlJBb3hRTURpN2hYaVN5UHhvVlVXNHBqMzBnSklwQkwKalh3aTZrRXBtL3JVYW92SndKODF1czA9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ0g3dTdDa3ZzR0xpNVIKYnJaYUM0R2NKa3BseHRjaENGM1Rrb0EyL05VL3Ezdi95ZlZnczR4dzB2aENCV0QwamhWUHI4cFVsV0dhRjlyTgo0ZWhFZ29nb1U3NDE3SkdtT0wyM0tLOWpYOHpRVm9MbUpvckw4Ukd3RHBIajBrcmxkeFcxZUJDVlRudmNHMGpIClY3WnAxTkJNLzVrV1JoRi9qVk5nQ3JEM3RNVWEwYVVCYnhwdmpHTzY0dEFaYVVuUHN4YVBxSW0rUStCNWltaEMKcGMwZjg5enJHT216NGVwUThUc0ZWQVAxNmNhLzBoTUYyMitpMXcwRHN2SGlUdkJRd2JiL0JERFdXclVnbHd3Kwp2R1F0alFWcXYwQWFzNGZ3S2hOQStMSTNJdUh0eURjUDhES0d3bkhha1VhUk9PMGsyUkgvM3lYVlE2TWZKZGlvCjJ4RUc3TTY5QWdNQkFBRUNnZ0VBQU1ZOVNZOEY5aUwrQzhWem15RWVWM1lvVlVWYm9XZmRlWElYR2Q4djRPZmsKbWFXMkJBOUM3dXhxcDhHNVFSRWRQVjdYdjZZQzB6OE9WQ0NGZklLMmVUYTRQNnJ3MCtaY1FVVHJlMWJEMXBZTApsSXUxbzd1RjM1NGlaSUp3NFJpTnh2K3g0QU45WEwxN1lrL1BOcTdSc1ROYzJCTXMyWGFEM3FrdkJyeFJqT1djCjd1bUxBZTdPQTBnb2NOOVJ2K3F0alByRmV6VUhkS0hyWisrUnZUeWxnWkdCVitLVXVDeW1JZENEWFdxVUFwVXAKcUo0R3dWbGlCREQ2NldXd3ppSVFxUXU0dFJmTERxdmRmQU8wUmxRcWNVOUdGUDF2TlIyTldZbnBkRVZVL0NuYQpTYmFDOWZWQ2pVeS9ZWDlIYXVPWjNRajFmVWVKVGRTcEtSaWRWKzI2Y1FLQmdRQzQ1bkZNL2lwZGlwbzZqNFBsCkVnaDJ1azlMdVNUak9SL1FDRFlETmdLSWozbTB6SjA1SUlTZkgzbUVQYzhMcERlWVd5VTNTaWhJbHFCRnhGSzAKWkxrZXRpa2wzK29BL2Zqdnc1YlI4aGZPQTNLbk9IV0d0K25mYVNYMWQva2ExSmJvbGYrNS9nNysrQ1Q3Sm1nWApTNzMzWFhQYWRGTXRwNmxZdjREZjVOMGhiUUtCZ1FDOE5ETGdUcytKRnB1cFVDc2VyL2c2VjBNcDU1emh2dW9PCjNNaDdjZlduREhsSTVYV0lnRVoxQ013Mmk1MUFLemNOTWxvZFVITU9yTU5hOEVKcFVKNEZoUFdQNzBPNmhMMjUKMHVpVEtpc3B6ZkI4bHV0SXhGWnlNZkZpMWlaZ3Z0L0diWEREa3FXeUJtL1lGZk1mRFk2SkQyTHRUdGxJczhMMwovaVIvQ3pSZ2tRS0JnRVFpZHVIZVR4SkZQdXdSY3BMNUFERndHa1JYSjJhcjZETXFzMnlmZkhPQ0cyRXFmVTFOCjFGRW1zZ3F2RkJyQUd0U0QwY1Q4Q0xnbStVeDhPZFhMd0FPM01KYUtXcHFlL0JxdVFtZC9CSktmNXFJRVJocXMKcnZ2cXJWZzFLNUJkZ25hV3Y3TjBFV2FYWGxsR0g5bGx5Y3piblJPRkJobXV6Tkt0VHZveVJlSkpBb0dCQUl2KwpVLzNRQWNZYVlBMlFpWktaR0k3bERCdW1vbWExYVV0RzVZWVZuY0gxb0Y0ZCtOQmhnb2RaMVBXWjRvMngxNUJrCmJPMnpRdktlaGU0bUczQlZQRVlrd2JpZ0pJUWdhelJIY3lMTTBqQ1ZkSlpvZUhtM09ncFZwaFY3OEM0MHJTWGYKa0dxWnNkRDd3c1E4aDQwSXU0YXVRRXIvUk5jMGlBbUtMTUducHYxUkFvR0FITVE0aVhWR1lNZ1Fhcm5ieUZXVQo2SkVXUWF5Z2t4L3lESUJWS01nM09xUkhZMXl1TWtEUGxVNEF4b0ZHc3QzUGJnb3hBbUQ3NWZ1Z0V0bEZTNDhVClpkQ1d2SlJsVFltNldhNytJZEtqZThXSWJudlhMODk0RWkvVjVQdC9hbDVjNzE5WW1UNUVrYmFOaWVmc1h5WDkKUjhrcXNETGw2aVdWdGorTCtXL0tqNzA9Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K
type: kubernetes.io/tls
###
# nginx.yaml 和 ingress,ingress更改域名
vim nginx.yaml
### 可以不改
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
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
        image: nginx:latest
        ports:
        - containerPort: 443
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
        - name: nginx-html
          mountPath: /usr/share/nginx/html
        - name: tls
          mountPath: /etc/nginx/ssl/
          readOnly: true
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-conf
      - name: nginx-html
        configMap:
          name: html-php
      - name: tls
        secret:
          secretName: nginx-tls
---
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  selector:
    app: nginx
  ports:
    - port: 443
      targetPort: 443
  type: ClusterIP
---
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
    - www.zxh.com
    secretName: nginx-tls
  rules:
  - host: www.zxh.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginxsvc
            port:
              number: 443
###
# 验证
kubectl apply -f ./
# 等待容器 Running
curl https://www.zxh.com
	# 如果不行
	curl https://<nginxsvc IP地址>
		# 如果不行,进入php容器
		php /usr/share/nginx/html/index.php
		# 查找那一层出问题
```

整合 yaml
```shell
# 整合，文件顺序不能出错
cat mysql-conf.yaml mysql.yaml php-conf.yaml html.yaml php.yaml tls.yaml nginx-conf.yaml nginx.yaml > helm.yaml
# 进入helm.yaml添加分割线
# 将之前部署的容器全部删除
kubectl delete ./
# 转换为helm格式
helmify -f helm.yaml zxh
# 修改
cd zxh/
vim values.yaml
# 复制index网页部分并删除
# 将密钥源文件粘贴
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062313889.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062322366.png)

修改 zxh/templates/helm. yaml 文件

将网页文件内容粘贴到此处，db_host修改为 IP
```shell
<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
$db_host = '10.100.0.2';
$db_port = getenv('DB_PORT') ?: '3306';
$db_name = 'zxh';
$db_user = 'root';
$db_pass = '123.com';
echo "Attempting to connect to: $db_host:$db_port<br>";
try {
    $dsn = "mysql:host=$db_host;port=$db_port;dbname=$db_name";
    $options = array(
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_TIMEOUT => 5, // 设置连接超时
    );
    $dbh = new PDO($dsn, $db_user, $db_pass, $options);
    echo '非常开心，数据库连接成功！！！<br>';
} catch (PDOException $e) {
    echo '恭喜恭喜，数据库连接失败~~~<br>';
    echo '错误信息： ' . $e->getMessage() . '<br>';
    echo '错误代码： ' . $e->getCode() . '<br>';
}
phpinfo();
?>
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062327101.png)

phpsvc 处添加指定 ip

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062331564.png)

mysqlsvc 处添加指定 IP

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062332131.png)

修改最后的 ingress 部分（secretName 新增变量）

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062333538.png)

更改结束后验证
```shell
helm install zxh .
# 查看是否Running
# 查看service IP 是否正确
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062340269.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062340312.png)

验证访问

```shell
kubectl port-forward --address 0.0.0.0 services/zxh-nginxsvc 8080:443
# 浏览器访问https://ip:8080/index.php
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408062356817.png)

打包
```shell
# kube01
helm package zxh
# 拷贝到kube02
scp zxh-0.1.0.tgz kube02:/var/www/html/charts/
```

搭建本地仓库

kube 02：
```shell
# 下载httpd
yum -yq install httpd
# create repo
mkdir /var/www/html/charts/
cd /var/www/html/charts/
# 查看是否有tgz包
ls
# 生成索引页文件，如果不是新仓库请忽略
helm repo index ./charts/
# 合并索引页文件，如果不是旧仓库请忽略
helm repo index ./charts/ --merge ./charts/index.yaml
```

kube 01：

```shell
# 添加仓库，旧仓库请忽略
helm repo add zxh http://10.15.200.242:/charts
# 更新仓库，新仓库请忽略
helm repo update zxh
# 查看仓库内容
helm search repo zxh
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408070004921.png)

```shell
# 下载并验证
helm install zxh/zxh --generate-name 
# 查看running情况 
# 访问
kubectl port-forward --address 0.0.0.0 services/zxh-1722960524-nginxsvc 8080:443
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408070011041.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408070010766.png)

小地球写入域名后可以用 www.zxh.com访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408070015305.png)



### 懒人部署包

[tgz 包下载](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/zxh-0.1.0.tgz)

z
拷贝到仓库进行后续操作即可，域名无法修改
