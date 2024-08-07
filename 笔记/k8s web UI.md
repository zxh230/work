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


******

