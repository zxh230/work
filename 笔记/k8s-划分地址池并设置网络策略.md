#### 要求 ：

> 1、创建新的 calico 地址池，要求容纳 node 节点 1000 个，每个节点容纳 pod 500 个<br />
> 2、使用上面地址池创建 5 个 Pod。且无法上网，但互相之间可以访问<br />
> 3、创建任意镜像的 deployment 副本 3 个<br />
> 4、做网络策略：deployment 的 pod 无法访问第一题中的地址池。但是第一题中地址池中的 pod 可以可以访问 deployment 的 pod

------

1. 由于需要容纳 1000 个节点，其中每个节点容纳 500 个 pod<br />
   所以：总共需要的 pod 数量为 1000 <节点数>*500 <pod数量> == 500000 个<br />
    如每个 pod 一个 IP 地址，则划分为 /16 （可容纳 65534 个 IP 地址<br />
2. 创建 5 个 Pod。且无法上网，但互相之间可以访问

```shell
# 创建地址池yaml
mkdir calico/
cd calico/
vim ippool.yaml
###
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: ippool2
spec:
  blockSize: 23
  cidr: 10.10.0.0/16
  ipipMode: Always
  natOutgoing: true
  disabled: false
###
# 部署
calicoctl apply -f ippool.yaml
# 创建pod，使用nginx镜像
vim nginx.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 5
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
###
# 部署
kubectl apply -f nginx.yaml
# 创建deployment部署文件
vim deployment.yaml
###
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      iptoip: deny-all
  template:
    metadata:
      labels:
        iptoip: deny-all
    spec:
      containers:
      - name: deployment
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
###
# 部署
kubectl apply -f deployment.yaml
# 创建NetworkPolicy策略
vim nonet.yaml
###
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-internet-egress
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector: {}
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-to-ippool
spec:
  podSelector:
    matchLabels:
      iptoip: deny-all
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-egress-traffic
spec:
  podSelector:
    matchLabels:
      iptoip: deny-all
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 192.168.0.0/16
###
# 部署
kubectl apply -f nonet.yaml
```

------

#### 验证

1. 验证 IP pool 地址池是否部署，划分是否正确
   ~~~shell
   calicoctl get ippool
   ~~~

    ![image-20240729091201611](https://gitee.com/zhaojiedong/img/raw/master/image-20240729091201611.png)

   ~~~shell
   calicoctl ipam show --show-block
   ~~~
   
    ![image-20240729091126399](https://gitee.com/zhaojiedong/img/raw/master/image-20240729091126399.png)
   
2. 验证 nginx 是否部署，地址网段是否正确
   ~~~shell
   kubectl infopod 
   ~~~

    ![image-20240726234530848](https://gitee.com/zhaojiedong/img/raw/master/image-20240726234530848.png)

3. 验证 networkpolicy 是否成功部署

   ~~~shell
   kubectl get networkpolicies
   ~~~

    ![image-20240726234629647](https://gitee.com/zhaojiedong/img/raw/master/image-20240726234629647.png)

4. 验证 nginx pod 是否可以上网

   ~~~shell
   kubectl exec -it nginx-576c6b7b6-z9hht -- curl www.baidu.com
   # 也可以一次验证所有 pod 是否可以上网
   kubectl exec -it nginx-576c6b7b6-{g2lc5, h8tnr, rz562, szdn4, z9hht} -- curl www.baidu.com
   ~~~

    ![image-20240726234931039](https://gitee.com/zhaojiedong/img/raw/master/image-20240726234931039.png)

5. 验证 deployment pod 是否可以访问 nginx pod

   ```shell
   kubectl exec -it deployment-857c475b4c-8vqq4 -- curl 192.168.197.197
   ```

    ![image-20240726235340828](https://gitee.com/zhaojiedong/img/raw/master/image-20240726235340828.png)

    ![image-20240726235559355](https://gitee.com/zhaojiedong/img/raw/master/image-20240726235559355.png)

   

6. 验证 deployment pod 是否可以访问物理机（==物理机可以临时安装 nginx 来提供访问端口，因为 nginx: latest 内没有 ping 命令==）

   ```shell
   # 访问物理机
   kubectl exec -it deployment-857c475b4c-8vqq4 -- curl 10.15.200.241
   ```

    ![image-20240726235717730](https://gitee.com/zhaojiedong/img/raw/master/image-20240726235717730.png)

   <HR align=center width=100% color=red SIZE=2>
   
   ### networkpolicy 策略详解
   
7. 第一段

   ```shell
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: deny-internet-egress
   spec:
     podSelector:
       matchLabels:
         app: nginx
     policyTypes:
     - Egress
     egress:
     - to:
       - podSelector: {}
   ###---###
   # 此部分定义了名为deny-internet-egress的网络策略
   # 使用 podSelector.matchLabels 设定了要应用该策略的pod为匹配所有带有app=nginx标签
   # 使用 Egress 配置出站流量
   # 使用 to.podSelector: {} 指向同一命名空间内的所有pod，意味允许到达该集群内的所有pod，但是无法到达外部，如：物理机，互联网
   # 总结------
   # 限制所有带有 app=nginx 标签的 Pod，使其只能向集群内的其他 Pod 发送流量，但不能访问集群外的任何网络（包括互联网）
   ```

8. 第二段
   ```shell
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: deny-to-ippool
   spec:
     podSelector:
       matchLabels:
         iptoip: deny-all
     policyTypes:
     - Ingress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app: nginx
   ###---###
   # 此部分定义了名为deny-to-ippool的网络策略
   # 匹配的标签为 iptoip=deny-all
   # ingress 设置了入站规则
   # from.podSelector.matchLabels 匹配只有来自 app=nginx 标签的pod的流量可以进入
   # 总结------
   # 匹配只有带有 app=nginx 标签的pod可以访问带有 iptoip=deny-all 标签的pod
   ```

9. 第三段

   ```shell
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: deny-egress-traffic
   spec:
     podSelector:
       matchLabels:
         iptoip: deny-all
     policyTypes:
     - Egress
     egress:
     - to:
       - ipBlock:
           cidr: 0.0.0.0/0
           except:
           - 192.168.0.0/16
   ###---###
   # 此部分定义了名为deny-egress-traffic的网络策略
   # 匹配带有标签 iptoip=deny-all 的pod
   # Egress 匹配出站规则
   # cidr: 0.0.0.0/0 允许去往所有网段的流量
   # except 除了指定的网段
   # 总结------
   # 所有带有 iptoip=deny-all 标签的 Pod 可以向除 192.168.0.0/16 网段外的任何 IP 地址发送流量
   ```

10. ==总结==

   使得带有 iptoip = deny-all 标签的 pod 只能接受来自来自有着  app = nginx 标签的入站(被访问)流量<br />
   同时，当出站(访问)流量目的地为任意网段时，只会拒绝 192.168.0.0/16 网段的流量<br />

   使带有 app = nginx 标签的所有 pod 均可以访问与其同集群/空间的任何 pod，但是无法出集群，也就无法访问互联网与物理机