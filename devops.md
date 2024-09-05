环境：
因为 k 8 s 主节点有污点不会调度 pod，所以提高从节点资源

k8s主节点：kube 01 (4 G 内存，4 核 cpu)  10.15.200.241

k8s从节点：kube 02 (8 G 内存，6 核 cpu)  10.15.200.242

docker 环境：kube 03 (4 G 内存，4 核 cpu)  10.15.200.243

配置 nfs
```shell
#kube02(nfs-server)
yum install nfs-utils
vim /etc/exports
###
/mydata/nfs/jenkins *(rw,sync,no_root_squash,no_subtree_check)
/mydata/nfs/pgsql *(rw,sync,no_root_squash,no_subtree_check)
/mydata/nfs/sonarqube *(rw,sync,no_root_squash,no_subtree_check)
###
# 创建目录
mkdir -p /mydata/nfs
mkdir /mydata/nfs/pgsql
mkdir /mydata/nfs/jenkins
mkdir /mydata/nfs/sonarqube
chmod 777 /mydata -R
# 重启nfs-server
systemctl restart nfs-server.service 
# 检查nfs
showmount -e 10.15.200.241
exportfs -a
exportfs -s
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831182610.png)

```shell
# kube01
# 创建配置目录
kubectl create ns devops
mkdir -p /mydata/devops/sonarqube/
cd /mydata/devops/sonarqube/
# 部署postgresql
vim postgresql.yaml
###
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pgsql-nfs
  namespace: devops
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: "managed-nfs-storage"
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /mydata/nfs/pgsql
    server: 10.15.200.242
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgress-data
  namespace: devops
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: "managed-nfs-storage"
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-sonar
  namespace: devops
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres-sonar
  template:
    metadata:
      labels:
        app: postgres-sonar
    spec:
      containers:
      - name: postgres-sonar
        image: registry.inspurcloud.cn/devops-cicd/postgres:v1
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "sonarDB"
        - name: POSTGRES_USER
          value: "sonarUser"
        - name: POSTGRES_PASSWORD
          value: "admin123456"
        volumeMounts:
          - name: data
            mountPath: /var/lib/postgresql/data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: postgress-data
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-sonar
  namespace: devops
spec:
  type: NodePort
  ports:
  - name: postgres-sonar
    port: 5432
    targetPort: 5432
    protocol: TCP
  selector:
    app: postgres-sonar
###
# 部署
kubectl  apply -f pgsql.yaml 
# 查看
kubectl get po -n devops
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831192232.png)

```shell
# 部署sonarqube
vim sonarqube.yaml
### 更改IP地址为nfs-server的IP地址
apiVersion: v1
kind: PersistentVolume
metadata:
  name: sonarqube-nfs
  namespace: devops
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: "managed-nfs-storage"
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /mydata/nfs/sonarqube
    server: 10.15.200.242
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sonarqube-data
  namespace: devops
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: "managed-nfs-storage"
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sonarqube
  namespace: devops
  labels:
    app: sonarqube
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sonarqube
  template:
    metadata:
      labels:
        app: sonarqube
    spec:
      #imagePullsecrets:
      #- name: harbor-secret
      initContainers: ##▒~H~]▒~K▒~L~V容▒~Y▒
      - name: init-sysctl
        image: registry.inspurcloud.cn/devops-cicd/busybox:v1
        command: ["sysctl","-w","vm.max_map_count=262144"]
        securityContext:
          privileged: true
      containers:
      - name: sonarqube
        image: registry.inspurcloud.cn/devops-cicd/sonarqube:10.1.0-community
        ports:
        - containerPort: 9000
        env:
        - name: SONARQUBE_JDBC_USERNAME
          value: "sonarUser"
        - name: SONARQUBE_JDBC_PASSWORD
          value: "admin123456"
        - name: SONARQUBE_JDBC_URL
          value: "jdbc:postgresql://postgres-sonar:5432/sonarDB"
        livenessProbe:
          httpGet:
            path: /sessions/new
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /sessions/new
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 30
          failureThreshold: 6
        volumeMounts:
          - mountPath: /opt/sonarqube/conf
            name: data
          - mountPath: /opt/sonarqube/data
            name: data
          - mountPath: /opt/sonarqube/extensions
            name: data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: sonarqube-data
---
apiVersion: v1
kind: Service
metadata:
  name: sonarqube
  namespace: devops
spec:
  type: NodePort
  ports:
  - name: sonarqube
    port: 9000
    targetPort: 9000
    protocol: TCP
  selector:
    app: sonarqube
###
# 查看
kubectl get po -n devops
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831204547.png)

```shell
# 部署jenkins
vim jenkins.yaml
###
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jenkins-nfs
  namespace: devops
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: managed-nfs-storage
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /mydata/nfs/jenkins
    server: 10.15.200.242
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: devops
spec:
  storageClassName: managed-nfs-storage
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins-admin
  namespace: devops
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: jenkins-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: jenkins-admin
  namespace: devops
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: devops
  labels:
    name: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      name: jenkins
  template:
    metadata:
      name: jenkins
      labels:
        name: jenkins
    spec:
      serviceAccountName: jenkins-admin
      hostNetwork: true
      containers:
        - name: jenkins
          image: registry.inspurcloud.cn/devops-cicd/jenkins:2.452-jdk17
          securityContext:
            privileged: true
            runAsUser: 0
          ports:
            - containerPort: 8080
            - containerPort: 50000
          env:
            - name: LIMITS_MEMORY
              valueFrom:
                resourceFieldRef:
                  resource: limits.memory
                  divisor: 1Mi
            - name: JAVA_OPTS
              value: -Xmx$(LIMITS_MEMORY)m -XshowSettings:vm -Dhudson.slaves.NodeProvisioner.initialDelay=0 -Dhudson.slaves.NodeProvisioner.MARGIN=50 -Dhudson.slaves.NodeProvisioner.MARGIN0=0.85
          volumeMounts:
            - name: jenkins-home
              mountPath: /var/jenkins_home
            - name: kubectl
              mountPath: /usr/bin/kubectl
      securityContext:
        fsGroup: 1000
      volumes:
      - name: jenkins-home
        persistentVolumeClaim:
          claimName: jenkins-pvc
      - name: kubectl
        hostPath:
          path: /usr/bin/kubectl
---
apiVersion: v1
kind: Service
metadata:
  name: jenkins-svc
  namespace: devops
spec:
  type: NodePort
  ports:
  - name: jenkins-svc
    port: 8080
    targetPort: 8080
    protocol: TCP
  selector:
    name: jenkins
###
# 部署
kubectl apply -f jenkins.yaml
# 查看
kubectl get po -n devops 
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831205516.png)

查看后可以删除前两个 pod，只保留 jenkins 缓解压力

配置 gitlab (docker 环境)
```shell
# 部署gitlab
vim docker-compose.yaml
### 
version: '3.1'
services:
  gitlab:
    image: 'registry.cn-qingdao.aliyuncs.com/xuxiaoweicomcn/gitlab:17.3.1-ce.0'
    container_name: gitlab
    restart: always
    environment:
      GITLAB_OMNIBUS_CONFIG:
        external_url 'http://10.15.200.243:28080'  # 更改为自己的IP地址
        #gtilab_rails['gitlab_shell_ssh_port'] = 8822
    ports:
      - '28080:28080'
      #- '8822:8822'
    volumes:
      - './config:/etc/gitlab'
      - './logs:/var/log/gitlab'
      - './data:/var/opt/gitlab'
###
# 部署
docker compose up -d
```

查看 jenkins 与 gitlab 网页

jenkins: 

查看 service 的端口号

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831215922.png)


访问任意 k8s 节点 IP+端口号

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831215937.png)

查看 jenkins 密码
```shell
kubectl logs -n devops jenkins-7d6c69f9ff-h7869 
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831224308.png)

==安装选择 (安装推荐的组件)==

安装失败则更改安装源
```shell
# kube02
vim /mydata/nfs/jenkins/hudson.model.UpdateCenter.xml 
### 替换为以下内容
<?xml version='1.1' encoding='UTF-8'?>
<sites>
  <site>
    <id>default</id>
    <url>https://mirror.esuni.jp/jenkins/updates/update-center.json </url>
  </site>
###
```

还是安装失败就放弃

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831225138.png)

选择继续

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831225257.png)

继续下一步---> 选择重启 Jenkins

查看日志，判断是否初始化完成

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831233517.png)

登录 jenkins

账户：admin
密码：<随机密码>

下载插件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831233753.png)

安装gitlab、git Parameter、kubernetes、gitee、Maven intergration、Publish Over SSH等插件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831235456.png)

安装失败则放弃---->重启 jenkins

将 maven 压缩包导入 jenkins 的 pv 目录中
```shell
# kube02(nfs-server)
tar -xf apache-maven-3.9.9-bin.tar.gz -C /mydata/nfs/jenkins/
cd /mydata/nfs/jenkins/
mv apache-maven-3.9.9 maven
ls
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901102004.png)

配置 JDK 与 maven 的路径

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901102347.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901102548.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901102614.png)

访问 gitlab（端口号 28080）

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240831220005.png)

密码：
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901104403.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901104504.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901104533.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901104657.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901104811.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901104845.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901104922.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901105027.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901105056.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901105140.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901105314.png)

==接下来每次更改都需要点击保存更改==

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901105405.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901105516.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901110914.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901110917.png)

在 kube 03 上创建对应目录

```shell
mkdir /done
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901111029.png)

保存

打开 IDEA

新建项目

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901122217.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901122313.png)

安装该插件，安装后需要登录才可以使用

选择登录账号

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901122750.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901122855.png)

去邮箱查看邮件
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901123007.png)

跳转到浏览器后，填写信息选择注册，等待登录成功

登录后新建项目

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901151751.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901151830.png)

新建 java 类，名称 controller.TestController

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901151905.png)

编辑文件
```java
package com.example.demo.controller;  
  
import org.springframework.web.bind.annotation.GetMapping;  
import org.springframework.web.bind.annotation.RestController;  
  
@RestController  
public class TestController {  
    @GetMapping("/test")  
    public String test() {  
        return "Hello jenkins";  
    }  
}
```
开始运行
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152213.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152239.png)

出现 spring 后浏览器访问 localhost: 8080/test

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152319.png)

将项目上传到 gitlab
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152405.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152456.png)

搜索不到转到设置--->插件，安装 gitlab

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152613.png)

测试时找不到 git 点击下载，等待下载安装完成后再次测试

测试完成后会显示版本

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152719.png)

保存确定后关闭设置界面

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152834.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901152959.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153102.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153248.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153347.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153427.png)

也可以点击生成，生成一个令牌

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905180811.png)


转到 gitlab 页面

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153510.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153614.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153644.png)

将复制的 url 粘贴到 IDEA 中

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153725.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153742.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153759.png)

到 gitlab 上查看

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901153831.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901154057.png)

生成 API

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901154401.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901154442.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901154501.png)

==复制后保存下来以免丢失==

转到 jenkins

新建任务

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901154929.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901155028.png)

用户名是之前在 gitllab 创建的用户名

密码是 API tocken，ID 与描述随便

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901155137.png)

添加后选择添加的密码，此时，连接报错消失

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901155251.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901155352.png)

```shell
clean package -Dskip test
```

立即构建

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901155541.png)

等待大量时间

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240901155657.png)

项目成功运行

在 jenkins 的 pv 中查看打好的包
```shell
# 将dome-2更改为自己的项目名
ls /mydata/nfs/jenkins/workspace/dome-2/target/
```

IDEA 中集成 docker 容器

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105017.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105033.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105057.png)

新建两个文件 (docker-compose. yml，Dockerfile)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105136.png)

```Dockerfile
# Dockerfile
FROM daocloud.io/library/java:8u40-jdk  
COPY demo.jar /usr/local/  
WORKDIR /usr/local  
CMD java jar demo.jar
```

```yml
# docker-compose.yml
version: '3.1'  
services:  
  demo:  
    build:  
      context: ./  
      dockerfile: Dockerfile  
    image: demo-1:v1.0  
    container_name: demo  
    ports:  
      - 8080:8080
```

demo 与自己的项目名称相同

修改 pom. xml 文件
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105454.png)

添加一行
```java
<finalName>demo</finalName>
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105513.png)

再次提交到 gitlab 仓库

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105915.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902105950.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902110009.png)

回到 jenkins 再次运行任务

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902114627.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902114622.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902115355.png)

配置项目

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902115701.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902122706.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902115740.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902115759.png)
保存后重新构建

构建完成后去 kube 03 查看镜像

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902122825.png)

修改 sonarqube 的部署文件

```shell
# 删除kube主节点的污点
# 修改文件
vim sonarqube.yaml
###
apiVersion: v1
kind: PersistentVolume
metadata:
  name: sonarqube-nfs
  namespace: devops
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: "managed-nfs-storage"
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /mydata/nfs/sonarqube
    server: 10.15.200.242
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sonarqube-data
  namespace: devops
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: "managed-nfs-storage"
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sonarqube
  namespace: devops
  labels:
    app: sonarqube
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sonarqube
  template:
    metadata:
      labels:
        app: sonarqube
    spec:
      nodeSelector:
        kubernetes.io/hostname: kube01  # 更改为自己的主节点
      initContainers:
      - name: init-sysctl
        image: registry.inspurcloud.cn/devops-cicd/busybox:v1
        command: ["sysctl","-w","vm.max_map_count=262144"]
        securityContext:
          privileged: true
      containers:
      - name: sonarqube
        image: registry.inspurcloud.cn/devops-cicd/sonarqube:10.1.0-community
        ports:
        - containerPort: 9000
        env:
        - name: SONARQUBE_JDBC_USERNAME
          value: "sonarUser"
        - name: SONARQUBE_JDBC_PASSWORD
          value: "admin123456"
        - name: SONARQUBE_JDBC_URL
          value: "jdbc:postgresql://postgres-sonar:5432/sonarDB"
        livenessProbe:
          httpGet:
            path: /sessions/new
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /sessions/new
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 30
          failureThreshold: 6
        volumeMounts:
          - mountPath: /opt/sonarqube/conf
            name: data
          - mountPath: /opt/sonarqube/data
            name: data
          - mountPath: /opt/sonarqube/extensions
            name: data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: sonarqube-data
---
apiVersion: v1
kind: Service
metadata:
  name: sonarqube
  namespace: devops
spec:
  type: NodePort
  ports:
  - name: sonarqube
    port: 9000
    targetPort: 9000
    protocol: TCP
  selector:
    app: sonarqube
###
# 部署
kubectl apply -f bbb.yaml
# 查看
kubectl get all -n devops -owide
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902173815.png)

jenkins 安装插件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240902175013.png)

访问 sonarqube 的端口号

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905191842.png)

初始用户名密码为 admin/admin，第一次登录需要修改密码

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905192034.png)

jenkins 添加 sonarqube 

生成令牌

下载中文插件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905204811.png)

重新启动服务

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905204905.png)

重启后再次登录

生成登录令牌

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905205833.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905205926.png)

复制并保留令牌

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905205944.png)

到 jenkins 中添加凭据

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905210114.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905210139.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905210201.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905210323.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240905210352.png)
