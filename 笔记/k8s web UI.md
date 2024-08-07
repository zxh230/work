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