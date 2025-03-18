# docker 网络构成

##### bridge 网络

none 网络：仅有 lo 接口，无法联网，用处：随机码，二维码...

查看 docker 网络

```shell
docker network ls
```
![image-20240712135828033](https://gitee.com/zhaojiedong/img/raw/master/image-20240712135828033.png)
host：	与宿主机使用相同的网络信息，用处：将容器视为网络上的节点

​				注意容器内的端口会被宿主机使用，有可能冲突

```shell
docker run -it --name aaa --rm --network host busybox:1.36 ip a
```

![image-20240712142225623](https://gitee.com/zhaojiedong/img/raw/master/image-20240712142225623.png)

joined：与另一容器使用相同的网络信息，用处：监控容器的网络信息

​				--network：contianer: ContianeName

```shell
docker run -itd --name test --network container:web busybox:1.36
```

![image-20240712143400286](https://gitee.com/zhaojiedong/img/raw/master/image-20240712143400286.png)

------

RHEL：企业版\开源收费\稳定  --  卫星服务器

centos-stream：滚动更新版 --  软件永远保持最新的测试版本

Ferdora：偏向于桌面，个人，软件迭代速度快  --  epel（仓库）

rockylinux：使用 RHEL 源码编译，免费开源，稳定

------

https://rpmfind.net 网站，拥有所有的 rpm 包（ferdora 的仓库）

------

```shell
yum -yq install epel-release    # 安装rprl仓库
```

```shell
brctl stp my_br0 on   # 打开对应网桥的stp服务
ifconfig my_br0 192.168.168.1/24 up   # 配置网关

```

veth peer将所有的空间连接到宿主机

bridge将所有的宿主机中的veth卡连接在一起

结论：

1. bridge是空间的网段的网关
2. 每个bridge是一个网段
3. 在相同的bridge卡中可以使用容器名作为dns解析

docker network网络驱动器

单主机网络
host： 使用主机的网络
bridge：默认的网络驱动器，不能用于集群，仅连接本地网卡
跨主机网络
ipvlan：		ipv4 和 ipv6 的寻址，识别二层的vlan标签
macvlan：	允许为容器分配 mac 地址，容器正常通讯
overlay：	覆盖网络，在bridge的基础上再创建容器网络，使用vxlan

```shell
# 创建一块网卡
docker network create --driver bridge my_net
# 查看网卡ip
brctl
ifconfig br-f05e8ba62574
```

![image-20240712155420418](https://gitee.com/zhaojiedong/img/raw/master/image-20240712155420418.png)
```shel
# 指定创建网卡的IP地址与网关
docker network create --driver bridge --subnet 172.86.86.0/24 --gateway 172.86.86.1 my_net2
###
--subnet设置子网
--gateway设置网关
###
# 查看IP地址
```

![image-20240712155702335](https://gitee.com/zhaojiedong/img/raw/master/image-20240712155702335.png)

为容器分配网卡

```shell
docker run -itd --name aaa --network my_net2 busybox:1.36 
docker exec -it aaa ip a
```

![image-20240712160152744](https://gitee.com/zhaojiedong/img/raw/master/image-20240712160152744.png)

可以联通网络

![image-20240712160301087](https://gitee.com/zhaojiedong/img/raw/master/image-20240712160301087.png)

可以为容器指定网卡以及IP地址

```shell

```

![image-20240712160604805](https://gitee.com/zhaojiedong/img/raw/master/image-20240712160604805.png)

==对应关系==

![image-20240712160819644](https://gitee.com/zhaojiedong/img/raw/master/image-20240712160819644.png)

==只有自定义网段才可以指定分配IP地址==

这里为新容器ccc指定网卡为之前创建的my_net网卡，由于创建此网卡的时候没有指定子网，所以不能指定容器分配的IP地址

![image-20240712161015210](https://gitee.com/zhaojiedong/img/raw/master/image-20240712161015210.png)

==同网段的容器之间可以使用容器名进行通讯==

<img src="https://gitee.com/zhaojiedong/img/raw/master/image-20240712161529578.png" alt="image-20240712161529578" style="zoom:80%;" />

==不同网段的容器之间可以ping通网关==

![image-20240712161928118](https://gitee.com/zhaojiedong/img/raw/master/image-20240712161928118.png)

### ==查看防火墙==

```shell
iptables-save
```

![image-20240712162819464](https://gitee.com/zhaojiedong/img/raw/master/image-20240712162819464.png)

==解释：==

- ==RELATED：不同协议的回包==

- ==ESTABLISHED：同协议同回包==

- ==ACCEPT：允许==

- ==DROP：丢弃==

- ==RETURN：拒绝==

|![image-20240712162839255](https://gitee.com/zhaojiedong/img/raw/master/image-20240712162839255.png)

==MASQUERADE：==

​	==SNAT：私网转公网ip实现上网==

​	==DNAT：公网 ip 转私网 ip 实现服务发布互联网==

==在iptables中，统称叫做MASQUERADE，自动将所有地址转换到联网的地址==

![image-20240712164714491](https://gitee.com/zhaojiedong/img/raw/master/image-20240712164714491.png)

-i 表示进入方向，-o 表示出口方向   ! 取反

``` shell
docker network connect my_net2 [容器名]   # 网卡连接容器
docker network disconnect my_net2 [容器名] # 断开网卡连接
docker network rm my_net my_net2
```

### docker 端口映射

```shell
docker run -d --name test -p 80 nginx:1.24   # 将容器的80端口映射到物理机
docker run -d --name web -p 80:80 nginx:1.24 # 将容器的80端口映射到物理机的80端口
```

![image-20240712171454781](https://gitee.com/zhaojiedong/img/raw/master/image-20240712171454781.png)

==映射后可以通过访问物理机相应的端口访问容器==

总结：
1，容器访问外部世界：NAT
2，外部世界访问容器：端口映射
