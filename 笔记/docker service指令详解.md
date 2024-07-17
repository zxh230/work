### docker service指令详解

#### docker service

```shell
docker service ''
	create  # 用来创建serevice单元
	inspect # 查看创建好的service信息
	logs    # 查看service或者其中的容器日志
	ls 		# 查看servide列表信息
	ps		# 
```





要求：

1，将三个docker node节点创建docker swarm集群环境

node01上创建overlay2网卡，IP地址段（50.X.Y.0/24）

基于scratch构建rockylinux9的base镜像，要求除了内部命令外，可以使用dnf curl wget ip ifconfig三条命令

将上面的镜像上传到node3中的私有仓库中，用户名为自己的名字，密码为xxx（当天指定）

2，使用第一题的创建的网络

docker swarm 的副本模式运行普罗米修斯 server镜像

docker swarm 的 global 模式运行 cadvisor 和node—exporter镜像

3 ，node 3创建bridge网络