
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