```shell
# 新建一个configmaps
kubectl create configmap tomcat-config --from-literal tomcat_port=8080 --from-literal server_name=my.tomcat.com
# 查看
kubectl get configmaps
# 查看详细信息
kubectl describe configmaps tomcat-config
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021003846.png)

```shell
# 输出为yaml文件格式
kubectl get configmaps tomcat-config -o yaml
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021004552.png)

```shell

```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021008482.png)
```shell
kubectl create configmap dir --from-file /root/configmap/
kubectl describe configmaps dir 
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021009564.png)

创建一个配置文件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021010111.png)

部署

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021010654.png)

改变configmap时，之前的配置不会发生变化

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021011924.png)

通过yaml文件创建configmap

```shell
vim mysql-conf.yaml 
###
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-conf
  labels:
    app: mysql
data:
  master.cnf: |
    [mysql]
    log_bin
    log_bin_trust
    mysql_name=mysql-a
  slave.cnf: |
    [mysql]
    super_read_only
    log_bin_trust_function_creators=1
###
# 部署后查看
kubectl describe configmaps mysql-conf
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021018904.png)

```shell
vim nginx.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: web
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
        env:
        - name: test_env
          value: testenv
        - name: server_name
          valueFrom:
            configMapKeyRef:
              name: tomcat-config
              key: server_name
        - name: server_port
          valueFrom:
            configMapKeyRef:
              name: tomcat-config
              key: tomcat_port
###
# 部署后查看变量

```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021050541.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021050929.png)

将configMap挂载到pod内（热更新）

```shell
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: web
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
        env:
        - name: test_env
          value: testenv
        volumeMounts:
        - name: nginxconfig
          mountPath: /tmp/config
      volumes:
      - name: nginxconfig
        configMap:
          name: cmfromdir
# 进入pod查看
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021101352.png)

挂载并改变权限
```shell
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: web
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
        env:
        - name: test_env
          value: testenv
        volumeMounts:
        - name: nginxconfig
          mountPath: /tmp/config
      volumes:
      - name: nginxconfig
        configMap:
          name: cmfromdir
          items:
          - key: www
            path: nginx_conf
          defaultMode: 0666
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021111891.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021111610.png)

