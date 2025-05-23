##### 要求：
1、在namespace default中使用Deployment部署pod 3个运行nginx，使用service 端口映射到clusterIP的8080端口
2、在namespace devtest中 使用Statefulset部署pod 3个 运行PHP，使用service 的clusterIP访问
3、在namespace opstest中，使用Statefulset部署pod 1个运行mysql
访问nginx的service的clusterIP地址，可以打开index.php的测试页面，及mysql的链接测试
******
```shell
# 创建作业目录
mkdir lnmp
cd lnmp
# 编写mysql.yaml文件
vim mysql.yaml
###
apiVersion: v1
kind: Namespace
metadata:
  name: opstest
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-deployment
  namespace: opstest
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
        - name: mysql-data
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  namespace: opstest
spec:
  type: ClusterIP
  clusterIP: 10.96.0.100
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
###
# 部署
kubectl apply -f mysql.yaml
# 等待下载完成
# 授权
kubectl exec -it -n opstest mysql-deployment-758f47ffdc-qzsjm -- mysql -uroot -p'123.com'
create user 'root'@'%.%.%.%' identified by '123.com';
grant all on *.* to 'root'@'%.%.%.%';
```
配置 php

```shell
# 编写 php.yaml 文件
vim php.yaml
###
apiVersion: v1
kind: Namespace
metadata:
  name: devtest
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: php
  namespace: devtest
spec:
  selector:
    matchLabels:
      app: php
  serviceName: "php"
  replicas: 3
  template:
    metadata:
      labels:
        app: php
    spec:
      containers:
      - name: php
        image: php:8.1-fpm
        ports:
        - containerPort: 9000
        volumeMounts:
        - name: php-web
          mountPath: /var/www/html
        command: ["/bin/sh"]
        args:
        - "-c"
        - |
          docker-php-ext-install mysqli pdo pdo_mysql && \
          mkdir -p /usr/share/nginx/html && \
          echo "<?php
              try {
                  \$dsn = 'mysql:host=10.96.0.100;dbname=zxh';
                  \$username = 'root';
                  \$password = '123.com';
                  \$options = array(
                      PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                  );

                  \$dbh = new PDO(\$dsn, \$username, \$password, \$options);
                  echo '非常开心, 数据库连接成功!!!\\n';
              } catch (PDOException \$e) {
                  echo '恭喜恭喜, 数据库连接失败~~~\\n';
                  echo '错误信息: ' . \$e->getMessage() . '\\n';
              }

              phpinfo();
              ?>" > /usr/share/nginx/html/index.php
          php-fpm
      volumes:
      - name: php-web
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: php
  namespace: devtest
spec:
  type: ClusterIP
  clusterIP: 10.96.0.101  # 确保这个 IP 在你的集群 IP 范围内且未被使用
  selector:
    app: php
  ports:
    - port: 9000
      targetPort: 9000
###
# 部署
kubectl apply -f php.yaml
# 等待部署完成
# 验证mysql与php
kubectl get pods -n devtest; kubectl get pods -n opstest
```

![](https://gitee.com/zhaojiedong/img/raw/master/202407312109391.png)

```shell
# 验证php是否可以访问
kubectl exec -it -n devtest php-0 -- bash
php /usr/share/nginx/html/index.php 
```
![](https://gitee.com/zhaojiedong/img/raw/master/202407312111187.png)

部署 nginx

```shell
# 编写 nginx.yaml
vim nginx.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: default
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
      - name: init-nginx-config
        image: busybox
        command:
        - /bin/sh
        - -c
        - |
          cat <<EOF > /etc/nginx/conf.d/default.conf
          server {
            listen 80;
            server_name localhost;
            root /usr/share/nginx/html;
            index index.php index.html index.htm;

            location ~ \.php$ {
              fastcgi_pass 10.96.0.101:9000;
              fastcgi_index index.php;
              include fastcgi_params;
              fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
            }
          }
          EOF
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
      - name: init-php-file
        image: busybox
        command:
        - /bin/sh
        - -c
        - |
          cat <<EOF > /usr/share/nginx/html/index.php
          <?php
          try {
              \$link = mysqli_connect('10.96.0.100','root','123.com');
              if(\$link) {
                  echo "非常开心, 数据库连接成功!!!\n";
              } else {
                  echo "恭喜恭喜, 数据库连接失败~~~\n";
              }
          } catch (mysqli_sql_exception \$e) {
              echo "恭喜恭喜, 数据库连接失败~~~\n";
              // 如果你想看到具体的错误信息，可以取消下面这行的注释
              // echo "错误信息: " . \$e->getMessage() . "\n";
          }
          phpinfo();
          ?>
          EOF
        volumeMounts:
        - name: nginx-html
          mountPath: /usr/share/nginx/html
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
        - name: nginx-html
          mountPath: /usr/share/nginx/html
      volumes:
      - name: nginx-config
        emptyDir: {}
      - name: nginx-html
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: default
spec:
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30050
  type: NodePort
###
# 部署
kubectl apply -f nginx.yaml
# 进行映射
kubectl port-forward --address 0.0.0.0 services/nginx-service 8080:80
# 浏览器访问 :8080进行访问
```
![](https://gitee.com/zhaojiedong/img/raw/master/202407312115170.png)












kubectl-infopod 脚本插件
替换或更改即可
```shell
#!/bin/bash
show_usage() {
    echo "使用方法:"
    echo "  kubectl infopod                     # 查询当前namespace的pods"
    echo "  kubectl infopod <pod_name>          # 查询匹配的pod"
    echo "  kubectl infopod <namespace_name>    # 查询指定namespace的pods"
    echo "  kubectl infopod ... -w              # 持续监视模式"
}

query_pods() {
    local query=$1
    local watch=$2
    local namespaces=$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}')
    local watch_flag=""
    
    if [ "$watch" = "true" ]; then
        watch_flag="-w"
    fi
    
    # 检查是否是namespace
    if echo $namespaces | grep -w -q "$query"; then
        echo "在该namespace中的pod: $query"
        kubectl get pod -n "$query" $watch_flag -o custom-columns=NAME:.metadata.name,IP:.status.podIP,STATUS:.status.phase,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
    else
        # 在所有namespace中查找匹配的pod
        local found=false
        for ns in $namespaces; do
            if kubectl get pod -n "$ns" "$query" &>/dev/null; then
                echo "Pod found in namespace: $ns"
                kubectl get pod -n "$ns" "$query" $watch_flag -o custom-columns=NAME:.metadata.name,IP:.status.podIP,STATUS:.status.phase,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
                found=true
                break
            fi
        done
        
        if [ "$found" = false ]; then
            echo "没有任何匹配的pod: $query"
            show_usage
        fi
    fi
}

watch_mode=false
args=()

# 解析参数
for arg in "$@"; do
    if [ "$arg" = "-w" ]; then
        watch_mode=true
    else
        args+=("$arg")
    fi
done

if [ ${#args[@]} -eq 0 ]; then
    # 无参数，查询当前namespace的pods
    kubectl get pod $([[ "$watch_mode" = true ]] && echo "-w") -o custom-columns=NAME:.metadata.name,IP:.status.podIP,STATUS:.status.phase,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
elif [ ${#args[@]} -eq 1 ]; then
    # 有一个参数，查询匹配的pod或namespace
    query_pods "${args[0]}" "$watch_mode"
else
    # 参数不正确，显示使用方法
    show_usage
    exit 1
fi
```