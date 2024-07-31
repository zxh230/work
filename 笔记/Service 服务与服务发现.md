

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
![](https://gitee.com/zhaojiedong/img/raw/master/202407311130104.png)
![](https://gitee.com/zhaojiedong/img/raw/master/202407311130559.png)
![](https://gitee.com/zhaojiedong/img/raw/master/202407311131397.png)
