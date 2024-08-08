#### Role 资源中常用的 verbs 权限：

get：读取资源对象的内容，但不包括列表。
list：列出某个资源类型的所有对象。
watch：监视资源对象的变化。
create：创建新的资源对象。
update：更新已有的资源对象。
patch：部分更新资源对象。
delete：删除资源对象。
deletecollection：删除资源对象集合。
proxy：代理请求到某个资源对象。
impersonate：模拟某个用户或服务账户进行操作。
post：发送数据到资源对象（例如 API 请求）。
put：完全替换资源对象。
bind：绑定资源（通常用于 ServiceAccount 和 Pod 绑定）。
escalate：升级权限（通常用于角色和权限管理）

```shell
# roledemo.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]			# 指定资源所属的 API 组。空字符串表示核心 API 组
  resources: ["pods"]		# 列出了允许的操作
  verbs: ["get","list","watch"]
# get：允许获取单个 Pod 的详细信息。
# list：允许列出命名空间中的所有 Pod。
# watch：允许监视 Pod 的更改。
```

clusterrole：适用于集群内的范围，可以授权：

集群范围内的资源点：比如node

非资源点：比如 /bealth

跨空间访问:kubectl get pod --all-namespace

```shell
# clusterrole.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get","list","watch"]
```

集群中唯一的超级管理员 Role 用户

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408081016861.png)

******

# binding

- Role binding
- clusterRole binding

### role binding

