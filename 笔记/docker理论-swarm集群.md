docker swarm结构：
	manager 节点  —>  work 节点
	manager 主要用作管理，可以对任何 work 节点下达指令
	manager 节点选举

manager 节点数只能是奇数（最大为7）
		leader 状态
例如：一个由三个 manager 节点组成的集群，最多容忍一个 manager 损坏
N个manager，最多允许 (N-1)/2 个manager损坏	

work：允许实例的主机（运行容器的主机）

service(manager 下达的指令) —— desired ——>  replicas(副本)
desired(期望值)，保障副本数量不变
service ：docker swarm最小单元

docker 运行对象：
		docker run：在本地运行
		docker service：在集群运行

replicas模式：副本模式，永远保证有确定的副本数量运行，通常运行服务器
global模式：全局模式，保证每个 node 都有一个副本，通常运行客户端

端口映射的模式：
	ingress：routing mesh 所有的节点 dockerd 进行监听，全局路由
	host：	传统 docker-proxy 端口映射，仅可访问本地容器

![image-20240716135526385](https://gitee.com/zhaojiedong/img/raw/master/image-20240716135526385.png)

> 初始化成功

```shell
# 查看tocken
 docker swarm join-token manager
 # docker02，03加入节点
 # SWMTKN...随机
 docker swarm join --token SWMTKN-1-5kgsxw5a6k2x5ziyb9wajaxgaiywk1b5lifyjk57h0a0woygyr-a2qhd6lidkzybcfzwdlpu1g3e 10.15.200.241:2377
 # 查看节点以及状态
 docker node ls
 # 降级为work节点
 docker node demote docker02
 # 升级为manager节点
 docker node promote docker02
 # 拉取镜像
 docker pull dockersamples/visualizer
 # 在manager节点上启动
 docker run -it -d -p 8888:8080 -v /var/run/docker.sock:/var/run/docker.sock dockersamples/visualizer
 # 浏览器访问
 http://10.15.200.241:8888
```

|<img src="https://gitee.com/zhaojiedong/img/raw/master/image-20240716144151036.png" alt="image-20240716144151036" style="zoom:50%;" />

```shell
# 集群中创建service
docker service create --replicas 3 --name web_server nginx:1.24
# 指定副本数量3个，名称web_server
# 查看service
docker service ls
# 查看service中运行的容器
docker service ps web_server
# 对于没有前台程序的容器，启动时需要运行任意前台程序
docker service create --replicas 1 --name bbos busybox:1.36 ping www.baidu.com
# service中的容器不可被删除
# 查看web_server的信息
docker service inspect web_server --pretty
# 手动弹性伸缩（调整副本数）
docker service scale web_server=6
# 滚动更新（交替式更新），更换镜像
docker service update --image nginx:latest web_server
# 调整更新参数
docker service update --replicas 6 --update-parallelism 2 --update-delay 30s web_server 
# 回滚（只能回滚最后两次更新）
docker service update --rollback web_server
# 
docker service update --image nginx:latest --update-failure-action pause --update-max-failure-ratio 0.3 --update-monitor 10s --update-order start-first web_server 
# 查看service服务端口
ss -tulanp |grep 7946
# 查看容器访问端口
ss -tulanp |grep 4789
# 增加端口映射8080>80(容器)
docker service update --publish-add 8080:80 web_server
# 也可以创建service的时候添加端口映射
docker service create --name web_server1 --publish 8080:80 --replicas 2 nginx:1.24
# 
docker service create --name myweb --publish published=8080,target=80,protocol=tcp,mode=host --mode global nginx:latest
#
docker exec -it myweb
```

```
docker/dnsrr/vip
replicas：副本模式：永远保证有确定的副本数量运行，通常运行服务端
global：全局模式：保证每个node都有一个副本，通常运行客户端
端口映射的模式
ingress：routing mesh：所有的节点dockerd进行监听，全局路由
host：传统docker-proxy端口映射，仅可以访问本机容器
docker service create --name myweb --publish published=8080,target=80,protocol=tcp,mode=host --mode global nginx:latest

docker service create --name myweb -p 8080:80 --replicas 3 busybox:1.36 sh -c "sleep 1d"
进入容器
docker exec -it myweb.3.kc6naid9iwny4e367mbldrc38 sh
链接后即可ip netns查看net卡
ln -s /var/run/docker/netns /var/run/netns
ip netns
```

