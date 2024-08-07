kube 01：

```shell
# 添加仓库并更新
helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/
helm upgrade --install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard --create-namespace --namespace kubernetes-dashboard
# 查看仓库内容
helm search repo kubernetes-dashboard
# pull
helm pull kubernetes-dashboard/kubernetes-dashboard
# 解压并修改
tar -zxf kubernetes-dashboard-7.5.0.tgz 
cd kubernetes-dashboard/
```

安装 kubernetes-dashboard
```shell
helm install kubernetes-dashboard-web . --namespace kubernetes-dashboard
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408070908610.png)

```shell
kubectl edit -n kubernetes-dashboard svc kubernetes-dashboard-kong-proxy 
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408070929942.png)


访问 \https://IP地址:40080

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408070929799.png)

```shell
# 生成token
vim test.yaml
###
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
--- 
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
###
# 生成
kubectl -n kubernetes-dashboard create token admin-user
# 粘贴到网页进行登录
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408071056415.png)

```shell
# 生成token
kubectl -n kubernetes-dashboard create token admin-user
# 创建一个serviceacctount
kubectl create serviceaccount sa1
```


******

```shell
# nginx.yaml
apiVersion: v1
kind: Pod
metadata: 
  name: web
spec:
  containers:
  - name: nginx
    image: nginx:1.24
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
```

```shell
# 指定serviceaccounts身份
# nginx.yaml
apiVersion: v1
kind: Pod
metadata: 
  name: web
spec:
  serviceAccountName: sa1
  containers:
  - name: nginx
    image: nginx:1.24
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
```
serviceaccounts 以挂载的方式挂载到容器中

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408071908732.png)

******

[JSON Web Tokens - jwt.io](https://jwt.io/)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408071911480.png)

在容器中查看 token

在  jwt. io 进行解密

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408071913263.png)

当删除 pod 时，其内的 token 也会发生变化

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408071916001.png)

默认手动创建的 token 有效期为一小时

指定 token 有效期
```shell
# 也可以手动指定有效期
kubectl create token sa1 --duration 8640h
```

创建永久有效 token

```shell
# secret
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: default
  annotations:
    kubernetes.io/service-account.name: "sa1"
```
部署后查看

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408071924394.png)

此时去网站解密，token 变为永久有效

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408071925513.png)

