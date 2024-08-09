部署 ELK 集群

提高三台虚拟机 cpu 至 6 核心

内存提高至 8 GB

查看 containerd 日志（位于/var/log/pods/）

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091642998.png)
```yaml
vim all.yaml
###
# 部署elasticsearch
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
      annotations:
        "cni.projectcalico.org/ipv4pools": "[\"pood2\"]"
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:7.17.10
        ports:
        - containerPort: 9200
        - containerPort: 9300
        env:
        - name: discovery.type
          value: single-node
        resources:
          requests:
            memory: "4Gi"
          limits:
            memory: "8Gi"
---
# 部署elasticsearch service
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
spec:
  type: NodePort
  ports:
  - port: 9200
    targetPort: 9200
    nodePort: 40001
  selector:
    app: elasticsearch
---
# 配置文件
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
data:
  filebeat.yml: |-
    filebeat.inputs:
    - type: filestream
      enabled: true
      id: containerd-log
      paths:
        - /var/log/pods/*/*/*.log
      fields:
        type_index: containerd-nginx
      fields_under_root: true

    output.logstash:
      enabled: true
      hosts: ["logstash:5044"]
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  labels:
    k8s-app: filebeat
spec:
  selector:
    matchLabels:
      k8s-app: filebeat
  template:
    metadata:
      labels:
        k8s-app: filebeat
      annotations:
        "cni.projectcalico.org/ipv4pools": "[\"pood2\"]"
    spec:
      tolerations:
       - key: "node-role.kubernetes.io/control-plane"
         operator: "Exists"
         effect: "NoSchedule"
      containers:
      - name: filebeat
        image: docker.elastic.co/beats/filebeat:7.17.10
        imagePullPolicy: IfNotPresent
        args: [
          "-c", "/etc/filebeat.yml",
          "-e",
        ]
        securityContext:
          runAsUser: 0
        resources:
          limits:
            cpu: 2000m
            memory: 1000Mi
          requests:
            cpu: 100m
            memory: 100Mi
        volumeMounts:
        - name: config
          mountPath: /etc/filebeat.yml
          readOnly: true
          subPath: filebeat.yml
        - name: containers
          mountPath: /var/log/pods/
      volumes:
      - name: config
        configMap:
          defaultMode: 0640
          name: filebeat-config
      - name: containers
        hostPath:
          path: /var/log/pods/
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kibana-config
data:
  kibana.yml: |
    server.port: 5601
    server.host: "0.0.0.0"
    elasticsearch.hosts: ["http://10.15.200.241:40001"]  #server1d ip
    i18n.locale: "zh-CN"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kibana
  template:
    metadata:
      labels:
        app: kibana
      annotations:
        "cni.projectcalico.org/ipv4pools": "[\"pood2\"]"
    spec:
      hostNetwork: true
      nodeName: kube03
      containers:
      - name: kibana
        image: docker.elastic.co/kibana/kibana:7.17.10
        ports:
        - containerPort: 5601
        volumeMounts:
        - name: config-volume
          mountPath: /usr/share/kibana/config/kibana.yml
          subPath: kibana.yml
      volumes:
      - name: config-volume
        configMap:
          name: kibana-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: logstash-config
data:
  logstash.conf: |
    input {
      beats {
        port => 5044
      }
    }

    output {
      elasticsearch {
        hosts => ["http://elasticsearch:9200"]
        index => "%{[type_index]}-%{+YYYY.MM.dd}"
      }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logstash
spec:
  replicas: 1
  selector:
    matchLabels:
      app: logstash
  template:
    metadata:
      labels:
        app: logstash
      annotations:
        "cni.projectcalico.org/ipv4pools": "[\"pood2\"]"
    spec:
      containers:
      - name: logstash
        image: docker.elastic.co/logstash/logstash:7.17.10
        args: [
          "-f","/usr/share/logstash/config/logstash.conf"
        ]
        ports:
        - containerPort: 5044
        volumeMounts:
        - name: config-volume
          mountPath: /usr/share/logstash/config/logstash.conf
          subPath: logstash.conf
      volumes:
      - name: config-volume
        configMap:
          name: logstash-config
---
apiVersion: v1
kind: Service
metadata:
  name: logstash
spec:
  type: NodePort
  ports:
  - port: 5044
    targetPort: 5044
  selector:
    app: logstash
---
apiVersion: crd.projectcalico.org/v1
kind: IPPool
metadata:
  name: pood2
spec:
  cidr: 20.32.0.0/16
  ipipMode: Always
  natOutgoing: true
  disabled: false
  nodeSelector: all()
###
```
开始部署 `kubectl apply -f all.yaml`
查看 IP 地址池

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091632321.png)

等待镜像下载完成
```shell
watch -n 1 "kubectl get pods -owide"
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091633059.png)

检查分发的 ip 是否属于自定义地址池

查看 service，configMap

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091635779.png)

在浏览器访问节点 IP 地址:40001

kube 01 (10.15.200.241)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091638033.png)

kube 02 (10.15.200.242)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091638055.png)

kube 03 (10.15.200.243)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091639707.png)
访问 kibana

由于 kibana 部署在 kube 03 节点，并且配置为 hostNetwork 模式，没有配置对应 service，所以可以直接访问 kube 03 的 IP 地址: 5601 进行访问

访问 10.15.200.243:5601

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091648675.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091649356.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091649138.png)

查看现有索引名称

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091650652.png)

配置

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091651585.png)

选择右边创建索引模式创建对应索引

名称：containerd

时间戳默认

确认后创建，回到主页

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091653033.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091653864.png)

成功显示出日志信息

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091653168.png)
