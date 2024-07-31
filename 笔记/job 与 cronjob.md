

```shell
apiVersion: batch/v1
kind: Job
metadata:
  name: job
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: job
          image: busybox:1.36
          imagePullPolicy: IfNotPresent
          command:
          - /bin/sh
          - -c
          - echo "zxh"
# kind: job  指代该任务为一次性任务
# restartPolicy: Never: 指定 Pod 的重启策略为 Never，意味着一旦容器完成（无论成功或失败），都不会重启
# 
```