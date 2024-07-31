
编写一次性任务 job
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
```


```shell
apiVersion: batch/v1
kind: Job
metadata:
  name: hanjob
spec:
  backoffLimit: 3
  activeDeadlineSeconds: 120
  ttlSecondsAfterFinished: 30
  parallelism: 2
  completions: 10
  completionMode: Indexed
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: hanjob
        image: busybox:1.36
        imagePullPolicy: IfNotPresent
        command:
        - /bin/sh
        - -c
        - echo "hello hansir, hi k8s1"
# backoffLimit: 3: 如果容器失败，最多重试 3 次
# activeDeadlineSeconds: 120: Job 的执行时间限制为 120 秒。如果未完成，Job 会被终止
# 
```