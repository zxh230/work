## job
### 编写一次性任务 job
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
### 增加参数
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
# ttlSecondsAfterFinished: 30: Job 完成后将在 30 秒后被自动删除。
# parallelism: 2: 并行运行的 Pod 数量是 2。这意味着最多可以有两个 Pod 同时运行。
# completions: 10: Job 需要完成 10 次才能被认为成功。这意味着总共有 10 个任务需要完成。
# completionMode: Indexed: 使用索引模式来运行任务，允许每个 Pod 都有一个唯一的索引编号
```
等待pod执行完成后查看
![](https://gitee.com/zhaojiedong/img/raw/master/202407310923648.png)
## cronJob
```shell
apiVersion: batch/v1
kind: CronJob
metadata:
  name: job
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: job
            image: busybox:1.36
            imagePullPolicy: IfNotPresent
            command:
            - /bin/sh
            - -c
            - echo "hello hansir, hi k8s1"
# schedule: "*/1 * * * *": 使用 Cron 表达式，表示每分钟运行一次这个任务
# restartPolicy: OnFailure: 如果容器失败，则重启 Pod
# ---
# 每分钟创建一个新的 Job，Pod 运行一个简单的命令，输出"hello hansir, hi k8s1"，如果任务失败，Pod 会自动重启
```
