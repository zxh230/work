指定 pod 运行用户的身份/uid

```shell
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  containers:
  - name: main
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    securityContext:
      runAsUser: 10000
```
