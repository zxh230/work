
> 要求：
>
> 1. deployment创建`nginx:latest`镜像，副本数量3个
>    pod标签为：`app=test`  部署空间为  `test`  空间标签为  `project=test ` 
>    亲和到节点kube01上。
> 2. deployment创建php镜像
>    副本数量3个
>    pod标签为：test=php，亲和到nginx的副本。
> 3. deployment创建php
>    副本数量1个
>    pod标签为：app=mysql，亲和到php的副本上。
>    ip地址为：10.10.10.10
> 4. 安装calicoctl

------

```shell
# 编写yaml文件部署nginx:latest
vim nginx_7_25.yaml
###
apiVersion: v1
kind: Namespace
metadata:
  name: test
  labels:
    project: test
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: test
  labels:
    app: test
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/hostname
                operator: In
                values:
                - kube01
      containers:
      - name: nginx
        image: nginx:latest
      tolerations:  
        - key: "node-role.kubernetes.io/control-plane"
          operator: "Equal"
          effect: "NoSchedule" 
###
# 开始部署
kubectl apply -f 7_25.yaml
# 查询命名空间以及其标签是否正确
# 1.查询是否存在 test 命名空间
kubectl get namespaces
# 2.查询其标签
kubectl get namespaces test --show-labels
# 3.查询其内是否有pod，以及查看运行状态
kubectl get pods -n test
# 4.查询 test 空间内pod的标签
kubectl get pods -n test --show-labels 
```

 ![image-20240725203605762](https://gitee.com/zhaojiedong/img/raw/master/image-20240725203605762.png "查询是否存在 test 命名空间")

 ![image-20240725203700924](https://gitee.com/zhaojiedong/img/raw/master/image-20240725203700924.png "查询其标签")

 ![image-20240725203733669](https://gitee.com/zhaojiedong/img/raw/master/image-20240725203733669.png "查询其内是否有pod，以及查看运行状态")

![image-20240725203801620](https://gitee.com/zhaojiedong/img/raw/master/image-20240725203801620.png "查询 test 空间内pod的标签")

------

```shell
# 开始编写部署php的yaml文件
vim php_7_25.yaml
# 该yaml文件会把php部署到与nginx副本相同空间的不同节点上
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-deployment
  namespace: test
spec:
  replicas: 3
  selector:
    matchLabels:
      test: php
  template:
    metadata:
      labels:
        test: php
    spec:
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - topologyKey: "kubernetes.io/hostname"
            labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - test
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Equal
        value: ""
        effect: NoSchedule
      containers:
      - name: php
        image: php:fpm
        imagePullPolicy: IfNotPresent
###
# 开始部署
kubectl apply -f php_7_15.yaml 
# 等待拉取镜像
kubectl get pods -n test -w
# 查看pod是否运行以及所在节点
kubectl get pods -n test -o wide
```

![image-20240725230902279](https://gitee.com/zhaojiedong/img/raw/master/image-20240725230902279.png "查看pod是否运行以及所在节点")

------

```shell
# 编写mysql的yaml文件
vim mysql_7_25.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-deployment
  namespace: test
spec:
  replicas: 3
  selector:
    matchLabels:
      test: php
  template:
    metadata:
      labels:
        test: php
    spec:
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - topologyKey: "kubernetes.io/hostname"
            labelSelector:
              matchLabels:
                app: test
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      containers:
      - name: php
        image: php:fpm
        imagePullPolicy: IfNotPresent
###
# 等待部署完成
# 查看所在节点以及标签
kubectl get pods -n test -o wide --show-labels
```

![image-20240725231124479](https://gitee.com/zhaojiedong/img/raw/master/image-20240725231124479.png '查看所在节点以及标签')

------

#### 重构infopod插件使得其更加功能化

效果图：
![image-20240725232030948](https://gitee.com/zhaojiedong/img/raw/master/image-20240725232030948.png '使用插件简单地查询pod以及namespace内的pod')

~~~shell
# 修改插件，路径可能不相同
vim /usr/bin/kubectl-infopod
###
#!/bin/bash

show_usage() {
    echo "使用方法:"
    echo "  kubectl infopod                     # 查询当前namespace的pods"
    echo "  kubectl infopod <pod_name>          # 查询匹配的pod"
    echo "  kubectl infopod <namespace_name>    # 查询指定namespace的pods"
    echo "  kubectl infopod ... -w              # 持续监视模式"
}

query_pods() {
    local query=$1
    local watch=$2
    local namespaces=$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}')
    local watch_flag=""
    
    if [ "$watch" = "true" ]; then
        watch_flag="-w"
    fi
    
    # 检查是否是namespace
    if echo $namespaces | grep -w -q "$query"; then
        echo "在该namespace中的pod: $query"
        kubectl get pod -n "$query" $watch_flag -o custom-columns=NAME:.metadata.name,IP:.status.podIP,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
    else
        # 在所有namespace中查找匹配的pod
        local found=false
        for ns in $namespaces; do
            if kubectl get pod -n "$ns" "$query" &>/dev/null; then
                echo "Pod found in namespace: $ns"
                kubectl get pod -n "$ns" "$query" $watch_flag -o custom-columns=NAME:.metadata.name,IP:.status.podIP,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
                found=true
                break
            fi
        done
        
        if [ "$found" = false ]; then
            echo "没有任何匹配的pod: $query"
            show_usage
        fi
    fi
}

watch_mode=false
args=()

# 解析参数
for arg in "$@"; do
    if [ "$arg" = "-w" ]; then
        watch_mode=true
    else
        args+=("$arg")
    fi
done

if [ ${#args[@]} -eq 0 ]; then
    # 无参数，查询当前namespace的pods
    kubectl get pod $([[ "$watch_mode" = true ]] && echo "-w") -o custom-columns=NAME:.metadata.name,IP:.status.podIP,NODE:.spec.nodeName,IMAGE:.spec.containers[0].image
elif [ ${#args[@]} -eq 1 ]; then
    # 有一个参数，查询匹配的pod或namespace
    query_pods "${args[0]}" "$watch_mode"
else
    # 参数不正确，显示使用方法
    show_usage
    exit 1
fi
###
~~~