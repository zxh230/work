#### 初始化容器：initContaier
用途：
1. init （initial）
   容器包含

临时容器：通过临时容器增加指令
postStat：容器创建成功后允许的任务，通常可以是资源部署和初始化

```shell
# 与宿主机共享文件
apiVersion: v1
kind: Pod
metadata:
  name: box1
  labels:
    app: rspod
spec:
  containers:
  - name: test1
    image: nginx:1.24
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
    lifecycle:
      postStart:
        exec:
          command: ["/bin/bash", "-c", "echo hello from postStart > /usr/share/nginx/html/index.html"]
      preStop:
        exec:
          command: ["/bin/bash", "-c", "echo goodbye from preStop > /usr/share/nginx/html/index.html"]
    volumeMounts:
    - name: message
      mountPath: /usr/share/nginx/html/
  volumes:
  - name: message
    hostPath:
      path: /mnt/
```

daemonset：
保证每个节点上只有一个pod
动态标签识别
滚动更新/手动更新


```shell
# 动态标签发现机制
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: cadvisor
spec:
  selector:
    matchLabels:
      name: cadvisor
  template:
    metadata:
      labels:
        name: cadvisor
    spec:
      nodeSelector:
        disk: ssd
      hostNetwork: true
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
      containers:
        - name: cadvisor
          image: cadvisor:v0.49.1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          volumeMounts:
            - name: rootfs
              mountPath: /roofs
              readOnly: true
            - name: sys
              mountPath: /sys
              readOnly: true
            - name: containerd
              mountPath: /var/lib/containerd/
              readOnly: true
            - name: disk
              mountPath: /dev/disk
              readOnly: true
      volumes:
        - name: rootfs
          hostPath:
            path: /
        - name: sys
          hostPath:
            path: /sys
        - name: containerd
          hostPath:
            path: /var/lib/containerd/
        - name: disk
          hostPath:
            path: /dev/disk
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202407301155257.png)
