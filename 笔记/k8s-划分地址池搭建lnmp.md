
将其中的密钥与证书编码替换为自己的（base64  \*. crt/\*. key）(忽略\\)

更改自己的名字（php-zxh\/nginx-zxh 这些）

nginx 配置文件和 ingress 更改为与证书域名相同的域名

php 网页指向自己的 mysql IP 地址

更改要求地址池


******
创建网页目录（mysql IP 地址，所有节点）
```shell
mkdir -p /nginx/canary/new
mkdir -p /nginx/stable/old
echo zxh > /nginx/stable/old/index.html
echo hansir > /nginx/canary/new/index.html
# 写入网页文件
vim /nginx/index.php
###
<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
$db_host = '10.15.200.243';
$db_name = 'zxh';
$db_user = 'root';
$db_pass = '123.com';
try {
    $dsn = "mysql:host=$db_host;port=$db_port;dbname=$db_name";
    $options = array(
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_TIMEOUT => 5,
    );
    $dbh = new PDO($dsn, $db_user, $db_pass, $options);
    echo '非常开心，数据库连接成功！！！<br>';
} catch (PDOException $e) {
    echo '恭喜恭喜，数据库连接失败~~~<br>';
    echo '错误信息： ' . $e->getMessage() . '<br>';
    echo '错误代码： ' . $e->getCode() . '<br>';
}
phpinfo();
?>
###
```

前置要求，calico 地址池

```yaml
vim ippool.yaml
###
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: ippool2
spec:
  cidr: 10.10.0.0/16
  ipipMode: Always
  natOutgoing: true
  disabled: false
###
# 部署
calicoctl apply -f ippool.yaml
```

写入部署文件（自由更改 name，编码，nginx配置文件，域名，地址池，端口号）
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: php-conf
data:
  www.conf: |
    user = www-data
    group = www-data

    ; The address on which to accept FastCGI requests
    listen = 0.0.0.0:9000

    ; Set the process manager
    pm = dynamic

    ; The number of child processes to be created when pm is set to static and the maximum number of
    ; child processes to be created when pm is set to dynamic or ondemand.
    pm.max_children = 5

    ; The number of child processes created on startup.
    pm.start_servers = 2

    ; The minimum number of idle processes.
    pm.min_spare_servers = 1

    ; The maximum number of idle processes.
    pm.max_spare_servers = 3
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: html-php
data:
  index.php: |
    <?php
    error_reporting(E_ALL);
    ini_set('display_errors', 1);

    $db_host = '10.15.200.243';
    $db_name = 'zxh';
    $db_user = 'root';
    $db_pass = '123.com';
    try {
        $dsn = "mysql:host=$db_host;port=$db_port;dbname=$db_name";
        $options = array(
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_TIMEOUT => 5, // 设置连接超时
        );
        $dbh = new PDO($dsn, $db_user, $db_pass, $options);
        echo '非常开心，数据库连接成功！！！<br>';
    } catch (PDOException $e) {
        echo '恭喜恭喜，数据库连接失败~~~<br>';
        echo '错误信息： ' . $e->getMessage() . '<br>';
        echo '错误代码： ' . $e->getCode() . '<br>';
    }
    phpinfo();
    ?>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-pod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: php
  template:
    metadata:
      labels:
        app: php
      annotations:
        cni.projectcalico.org/ipv4pools: '["10.10.0.0/16"]'
    spec:
      containers:
      - name: php
        image: php:8.1-fpm
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9000
        env:
        - name: DB_HOST
          value: "mysqlsvc"
        - name: DB_PORT
          value: "3306"
        command: ["/bin/sh"]
        args:
        - "-c"
        - |
          docker-php-ext-install mysqli pdo pdo_mysql &&           mkdir -p /usr/share/nginx/html &&           php-fpm
        volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html/
        - name: conf
          mountPath: /usr/local/etc/php-fpm.d/www.conf
          subPath: www.conf
      volumes:
      - name: html
        configMap:
          name: html-php
      - name: conf
        configMap:
          name: php-conf
---
apiVersion: v1
kind: Service
metadata:
  name: php-zxh
spec:
  type: ClusterIP
  clusterIP: 10.10.0.1
  selector:
    app: php
  ports:
    - port: 9000
      targetPort: 9000
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-conf
data:
  aaa.conf: |
    server {
      listen 443 ssl;
      server_name www.zxh.com;
      root /usr/share/nginx/html;
      index index.php index.html index.htm;
      ssl_certificate /etc/nginx/ssl/tls.crt;
      ssl_certificate_key /etc/nginx/ssl/tls.key;
      error_page 400 /stable/old;


      location /canary/new {
        if ($http_vip = "user") {
        return 301 /stable/old;
        }
            root /usr/share/nginx/html;
            index index.html;
            error_page 400 /canary/new;
        }

      location /stable/old {
            root /usr/share/nginx/html;
            index index.html;
            error_page 400 /stable/old;
        }

      location / {
      if ($http_vip = "user") {
       return 301 /stable/old;
        }
      return 301 /index.php;
      }

      location ~ \.php$ {
      if ($http_vip = "user") {
       return 404;
      }
        fastcgi_pass 10.10.0.1:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
      }
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: nginx-tls
data:
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURPVENDQWlHZ0F3SUJBZ0lVQzBYOXorVE5MTG1kdFpXTE8ycTdVNjJwbThFd0RRWUpLb1pJaHZjTkFRRUwKQlFBd0xERVVNQklHQTFVRUF3d0xkM2QzTG5wNGFDNWpiMjB4RkRBU0JnTlZCQW9NQzNkM2R5NTZlR2d1WTI5dApNQjRYRFRJME1EZ3dPREE1TWpRek4xb1hEVEkxTURnd09EQTVNalF6TjFvd0xERVVNQklHQTFVRUF3d0xkM2QzCkxucDRhQzVqYjIweEZEQVNCZ05WQkFvTUMzZDNkeTU2ZUdndVkyOXRNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUYKQUFPQ0FROEFNSUlCQ2dLQ0FRRUEwamNlaWxwQnE4TXByTW13NlJ3bG5pUDRpdGxsYjJWQndONVRLeVNwYndFQQo3MzhSVmttMEdYUHlBSUdJNWE3LzB5TG9iTFpRZDloZUxGTEk5MjRwbjdjNjc4RjNmSTdlMFVCaXE1UDdicXhyCjk0VkdZOTlvWmpsSGNKQjdDdGZ6anhhVGxIMlBUbXBaaWFvRXdRRW1xRFU3WTI4QlpaZkNmYTFBZWRaQzJBREIKR081VERSN0pjRzRXei9wdzVYYnZaL1NtSW40bUZYeWlHVElVcTYya2U2UEZCbW16RUMzb3Y5RE1DNlZWQlZZUQptRjRpZDA5bDllU1RKVkFQczdvN1ltUzhCWUtCR3JsZnVkMjNYdlNXNjNpRG5vajlSY2JVM24yZHdhRTJHWXBoClRkS2hjVGhoSUdVdmhPN0ptWmJ2MHh6OVJpa1JJMTV0NzVBQWZQU0hXd0lEQVFBQm8xTXdVVEFkQmdOVkhRNEUKRmdRVVowZEVUaVYwRkRYUjAyK3dKNEhSMHJXcDZCVXdId1lEVlIwakJCZ3dGb0FVWjBkRVRpVjBGRFhSMDIrdwpKNEhSMHJXcDZCVXdEd1lEVlIwVEFRSC9CQVV3QXdFQi96QU5CZ2txaGtpRzl3MEJBUXNGQUFPQ0FRRUFDZ2w1CnBhWllQUDVVdzA3QlpINlBRRkFIZDI5ZlRpd0MwYk1VMzBhc1ZhSjlmS0g4OXlITEk5MmJ1aHNTWEJWM256Q2IKbjZzdVh1UG93c0dZZUdQajFVUjZoU0FSOXAvSWlBVGk1SlhlUEg3VzRXK203M3ZMZWxOT0ZVN2JHSEcrSU5WVgp5MFRuZ3BwcjNReWVmanFHblpIcnZ3ZkFDV3R0S0ZJWG1ZTy9ON21OTmRnUzA5MEdhVzRYcVhIZ1FhUXRnNTZFCkRRZ2JGWXBVdk9PR1h6ZkwzZFc3MmJmWndGYW91dlhUcFJmUzRRdE0yTkxtT3ZiT1FmYnB3cjljVGlRaGpqMU8KUG8rUzM3bzczRmVXY3cxMDJNbnlWcFlqWnpNdnFZSGFKMzRWOTJPb3U0ZndzcVZvY044S1JNV1g3ckFkTEsxKwpTUkpDMmUzbCtxWDVLTjd4emc9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRRFNOeDZLV2tHcnd5bXMKeWJEcEhDV2VJL2lLMldWdlpVSEEzbE1ySktsdkFRRHZmeEZXU2JRWmMvSUFnWWpscnYvVEl1aHN0bEIzMkY0cwpVc2ozYmltZnR6cnZ3WGQ4anQ3UlFHS3JrL3R1ckd2M2hVWmozMmhtT1Vkd2tIc0sxL09QRnBPVWZZOU9hbG1KCnFnVEJBU2FvTlR0amJ3RmxsOEo5clVCNTFrTFlBTUVZN2xNTkhzbHdiaGJQK25EbGR1OW45S1lpZmlZVmZLSVoKTWhTcnJhUjdvOFVHYWJNUUxlaS8wTXdMcFZVRlZoQ1lYaUozVDJYMTVKTWxVQSt6dWp0aVpMd0Znb0VhdVYrNQozYmRlOUpicmVJT2VpUDFGeHRUZWZaM0JvVFlaaW1GTjBxRnhPR0VnWlMrRTdzbVpsdS9USFAxR0tSRWpYbTN2CmtBQjg5SWRiQWdNQkFBRUNnZ0VBYUVFaTJkM0tYUHVVOHhjeU1HSWZ1KzYrQ0dxcDFsWERCdnFjQjdVT2ZMbGsKTStMeWY3ZGM1UlN1TEJjU0JFdEduL2xiaVBMZ05KZXZtTTdUMFhhbW1RbmY1bUV1TjYySmp3Q2VEdGI4NXhZSApFOEphdHhSbzYrMnpZdjJjc0RPS25PZkcrR2xQQmNaVHNxVUo1NGlCR2dJUWVvOW1nM0tBNkNCZzdpdlhpZFRyClAyNEZmQitEKzBabW9wYko5dWNNV0ZnKzFEVFpKNUJWMFNucXBzNklnazRDNXJhTG8rNVdWMEs2emd0TkwvYjMKT1d5c3hUMUY5c0s4SFlTeWFHR0VnUzAxSFg1eUs3TjJlenc2QW9xcjQ2K1M2Zkdrcnk1bzNlY3d4SDFneTZOUgp0M2VQL2w5UllOZXFGR3Y3dnZrZnZweFlrTmFIQnJFMHZuaHVHTll1cVFLQmdRRFlBbVRnVWpkY29NdEdSZUVkClV6U3JsZzJtRkQzOHpVOCsvcmZUbSswbmttRi92clFuYnR5UkY1SmcyM1l0K3NjRWJOZUtYRGViSk9URW5DRWUKZWJVeFBETnNxMVMyQnY4NFJyYzR6ZlB6d3NmeHVFUlVmRGtiMDROY3hzYTlTNGV1TUkxdkhpRTlmZXpldU5pNwpPZVBQNzdub2t3bEdEeWxFRUZtU3hYa1NTUUtCZ1FENUloN3YrV1lOUU5qZjJlRDFpOWp3M0FuWCt6bFhhZ3FtClNkWUV4VCtVNWxjdE8yRVR0Nk92Nmh6bmlwSnNmUk5HRHRFL2tKeDJtVDdEWG9QUWFzOWtHV0ZQVkx0ZmFoNFUKV2lRMFUzbW5UNVpUUTArSkZ5aUEveG1BZENiSGd6eGZCMGtKWGtTem85a1dybDVKM1M2cHNzUU1lclNVK0lsTgpoYzZpU2Y3TWd3S0JnUUNuYTN1YUxiOEJDUk5rUFFjVXZvZkZNZ0VVSnY1QWNUU3BvNjBBMHdyRnIvdm5rZng1Cno4QWVxTUZvVnRETEpHS2FPRzM2ckN6aEQ0Qk1McUt3eHk0N29laE5vcUYrai8vQ00zVVJEdmUwaDlTR3NnWXIKNFRnMkxBTFZwcThreW1TNENxT2theHJpV1RaOURaSFYwekdSMmNFaTFNdk1SRFg4cmh0dTJhVlVHUUtCZ1FEZgpXRENHRUg3bHlNbmt2TTVKTTR0VU90OTBTaHVZKzA3Nnp0ellRQUVGT3c3U1ZSWnRkOGQrRUpMREhONng5ZHRPCmhrQWZEVVRIcWhDelUwczJrRnJHc1Y0a29hQ3RKRlE5Q0tiR1prTjh0QVBmTjB2WmFmSjgycldCRENBcjRzSS8KcXlkV0I3WHRtaWtuaFVDd1ZXTGM3WStHWkliNXVtcFZIbTBsM3RKWGd3S0JnQXV3MFQ1T0JadjF1czBNTDlNRQp3cnZkbXJuQ2lJSlU0aktCT0N1ZFN5YnRIYitzNlJCSVFsRDdjOXZ6RGsyRVdJaE9oOFpRei9KSVFMdzV2UXA3CmM0a2ZRUkc3SnNEbTV6TEZJOG5sdkZ0RnBnVDRWYllaR0U5cXZmcnNJdHFWZTFrZ0x5S0Q2Smh2ejByajI5RksKUmwxR2VtZkcvUlJJWDBQWUhqWTNuL2hHCi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K
type: kubernetes.io/tls
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
      annotations:
        cni.projectcalico.org/ipv4pools: '["10.10.0.0/16"]'
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 443
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
        - name: tls
          mountPath: /etc/nginx/ssl/
          readOnly: true
        - name: nginx-web
          mountPath: /usr/share/nginx/html
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-conf
      - name: tls
        secret:
          secretName: nginx-tls
      - name: nginx-web
        hostPath:
          path: /nginx
          type: Directory
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-zxh
spec:
  selector:
    app: nginx
  ports:
    - port: 443
      targetPort: 443
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "https"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - www.zxh.com
    secretName: nginx-tls
  rules:
  - host: www.zxh.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-zxh
            port:
              number: 443
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingresa
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - zxh.com
    secretName: nginx-tls
  rules:
  - host: zxh.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-zxh
            port:
              number: 443
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rewrite-zxh
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/rewrite-target: www.zxh.com
spec:
  ingressClassName: rewrite-nginx
  rules:
  - host: "zxh.com"
    http:
      paths:
      - pathType: Prefix
        path: /
        backend:
          service:
            name: nginx-zxh
            port:
              number: 443
```
部署后访问：

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408082014396.png)

******

第三题[[k8s-部署ELK集群]]

略

******

第四题

编写 allinone. yaml

```shell
vim all-in-one.yaml
### 无需做任何修改
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: tomcat
  namespace: default
spec:
  serviceName: "tomcat-svc"
  replicas: 3
  selector:
    matchLabels:
      app: tomcat
  template:
    metadata:
      labels:
        app: tomcat
        env: restricted  # 添加标签
    spec:
      containers:
      - name: tomcat
        image: tomcat:latest
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: webapps-volume
          mountPath: /webapps
        - name: webapps-dist-volume
          mountPath: /webapps.dist
        resources:
          requests:
            cpu: "1000m"
            memory: "500Mi"
          limits:
            cpu: "1000m"
            memory: "500Mi"
        command: ["/bin/sh"]
        args: ["-c", "cp -r /usr/local/tomcat/webapps.dist/* /usr/local/tomcat/webapps/ && /usr/local/tomcat/bin/startup.sh && sleep 1d"]
      volumes:
      - name: webapps-volume
        emptyDir: {}
      - name: webapps-dist-volume
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: tomcat
spec:
  type: ClusterIP  # Headless service
  selector:
    app: tomcat
  ports:
    - port: 8080
      targetPort: 8080
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-tomcat-0
spec:
  podSelector:
    matchLabels:
      statefulset.kubernetes.io/pod-name: tomcat-0
  policyTypes:
    - Ingress
    - Egress
  ingress: []  # 不允许任何入站流量
  egress: []   # 不允许任何出站流量
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-net
spec:
  podSelector:
    matchLabels:
      app: tomcat
  policyTypes:
    - Egress
  egress:
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8
        - ipBlock:
            cidr: 172.16.0.0/12
        - ipBlock:
            cidr: 192.168.0.0/16
    - to:
        - namespaceSelector: {}  # 允许访问集群内的所有命名空间
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tomcat-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: tomcat
  minReplicas: 3
  maxReplicas: 8
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 20
###
```

部署后测试

编写测试脚本

```shell
vim index.sh
###
#!/bin/bash
# 获取 tomcat Pods 的列表
pods=$(kubectl get pods -o custom-columns=:metadata.name | awk '/tomcat-/')
# 记录处理的 Pod 数量
count=0
# 逐个处理每个 Pod
for pod_name in $pods
do
  # 生成不同的内容
  content="This is container $pod_name"
  # 写入网页内容，使用 printf 以避免编码问题
  kubectl exec -it $pod_name -- sh -c "echo '${content}' > /usr/local/tomcat/webapps/ROOT/index.jsp"
  # 增加计数器
  count=$((count + 1))
done
echo "Content written to $count containers."
###
```
给与执行权限后运行，输出如下信息：

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090100474.png)

提示成功写入了三个容器的网页文件

访问测试：

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090104817.png)

==--max-time 设定 curl 访问的总超时时间，一般情况下本地互相访问不会超过 5 秒==

转换为 helm

```shell
# 转换
helmify -f all-in-one.yaml tomcat-zxh
# 修改文件
vim templates/all-in-one-tomcat.yaml
```
修改 NetworkPolicy 部分

在 matchLabels 部分添加变量（变量名为*.fullname）

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090212443.png)

修改 StatefulSet 部分

删除多余变量

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090215113.png)

下方 service 部分

删除多余变量

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090217864.png)

增加防止被驱离

```shell
tolerations:
- key: node-role.kubernetes.io/control-plane
  operator: Exists
  effect: NoSchedule
- key: node.kubernetes.io/disk-pressure
  operator: Exists
  effect: NoSchedule
- key: node.kubernetes.io/memory-pressure
  operator: Exists
  effect: NoSchedule
- key: node.kubernetes.io/network-unavailable
  operator: Exists
  effect: NoSchedule
- key: node.kubernetes.io/not-ready
  operator: Exists
  effect: NoSchedule
- key: node.kubernetes.io/pid-pressure
  operator: Exists
  effect: NoSchedule
- key: node.kubernetes.io/unreachable
  operator: Exists
  effect: NoSchedule
- key: node.kubernetes.io/unschedulable
  operator: Exists
  effect: NoSchedule
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090239317.png)


修改完成后安装部署

```shell
# 确保当前目录下有values.yaml文件
helm install zxh .
```

验证访问

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090207192.png)

验证轮询

```shell
# 此处应为svc IP:8080
for h in $(seq 1 100)
do
curl 10.10.125.22:8080 --max-time 5
done
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090207091.png)


监控弹性伸缩

```shell
# 提高cpu压力
kubectl exec -it zxh-tomcat-zxh-tomcat-0 -- dd if=/dev/zero of=/dev/null
# 以秒为单位执行命令，监控pod数量
watch -n 1 "kubectl get pods"
# 以秒为单位执行命令，监控pod数量
watch -n 1 "kubectl get hpa"
```

效果图：

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090142585.png)

打包并上传仓库

kube 01：

```shell
# 打包,tomcat-zxh为目录
helm package tomcat-zxh
```

kube 03:
```shell
# 安装apache，启动并开机自启，创建仓库目录
yum -y install httpd; systemctl enable httpd; systemctl start httpd; mkdir /var/www/html/charts/
# 拷贝命令
scp kube01:/usr/local/sbin/helm /usr/local/sbin/
# 授权
chmod +x /usr/local/sbin/helm 
# 生成索引页并拷贝文件
helm repo index /var/www/html/charts/; scp kube01:/root/homework/kaoshi/four/tomcat-zxh-0.1.0.tgz /var/www/html/charts/
# 查看索引文件
cat /var/www/html/charts/index.yaml
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090227150.png)

kube 01：

```shell
# 添加仓库
helm repo add kube03 http://10.15.200.243:/charts
# 查看仓库以及内容
helm repo list;
helm search repo kube03
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408090231697.png)
