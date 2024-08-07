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
vim values.yaml 
```

