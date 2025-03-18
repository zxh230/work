
```shell
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: nginx
```
查看serviceIP地址，通过访问serviceIP地址的指定端口可以转发到代理pod
![](https://gitee.com/zhaojiedong/img/raw/master/202407311130104.png)
将pod扩展为6个副本，查看ip
![](https://gitee.com/zhaojiedong/img/raw/master/202407311130559.png)
查看service代理的所有IP地址
![](https://gitee.com/zhaojiedong/img/raw/master/202407311131397.png)

```shell
# 查看pod的dns策略
kubectl explain pod.spec.dnsPolicy
```
```shell
hostNetwork: true
dnsPolicy: ClusterFirstWithHostNet
# hostNetwork: true 使用节点网络
# dnsPolicy: ClusterFirstWithHostNet 即使Pod在宿主机网络中运行，Kubernetes集群DNS解析仍然优先
```
修改Cluster网段的IP
```shell
# 进入配置文件
vim /etc/kubernetes/manifests/kube-apiserver.yaml
```
![[Pasted image 20240801101451.png]]
```shell
# 更改为10.10.100.100/16
# 重启
systemctl daemon-reload 
systemctl restart kubelet.service
```
```shell
apiVersion: v1
kind: Service
metadata:
  name: nginxsvc
spec:
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: nginx
  externalIPs:
  - 10.15.200.110
# externalIPs 列出了Service可以绑定的外部IP地址
```
```shell
modprobe -- ip_vs
modprobe -- ip_vs_sh
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
yum -yq install ipset ipvsadm
kubectl rollout restart daemonset --namespace kube-system kube-proxy

```