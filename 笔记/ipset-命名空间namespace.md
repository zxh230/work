### 网络隔离理论

添加一对以太网连接设备，默认情况下只能相互进行访问

veth   —连接—>  peer

### 命名空间基础命令

```bash
ip netns add  [命名空间名称]    # 创建一个命名空间
ip netns exec [命名空间名称]    # 在命名空间内使用命令进行配置
ip netns list                  # 查看已有的命名空间列表与id
ip -all netns delete           # 删除所有命名空间
ip netns delete [命名空间名称]  # 删除指定的命名空间
ip netns identify [PID]        # 查看指定PID进程的命名空间
ip netns pids namespace1       # 查找使用此命名空间作为主要网络命名空间的进程
ip netns monitor               # 监控命名空间的添加或删除（只能监控添加或删除）,
                               # 可以指定命名空间以及其中的接口
### 扩展
ip netns exec [命名空间名称] bash   # 进入命名空间
```

### 配置网络命名空间

```bash
ip netns add aaa
ip netns exec aaa ip a
```

!https://gitee.com/zhaojiedong/img/raw/master/202407051659805.png

<LOOPBACK>表示网络接口

新添加的loopback接口默认被封装，需要解封装才能进行通信

```bash
ip netns exec aaa ip link set dev lo up   # 解封装aaa空间的lo网卡
ip netns exec aaa ip a   # 查看aaa空间的lo网卡的IP地址
# 此时可以使用ping进行通信
ip a  # 查看网卡信息
```

!https://gitee.com/zhaojiedong/img/raw/master/202407051709608.png

```bash
ip link add veth0 type veth peer name veth1  # 配置veth-->peer连接
ip link set veth1 netns aaa  # 将veth1网卡放入aaa空间中
# 再次ip a查看网卡信息发现veth0连接对象变成了interface6接口
```

!https://gitee.com/zhaojiedong/img/raw/master/202407051726203.png

```bash
ifconfig veth0 1.1.1.2/24 up   # 启动网卡并设置IP为1.1.1.2
```

!https://gitee.com/zhaojiedong/img/raw/master/202407051715677.png

```bash
ip netns exec aaa ifconfig veth1 1.1.1.1/24 up  # 将aaa空间内的网卡veth1启动并设置ip
```

查看网卡与路由信息

!https://gitee.com/zhaojiedong/img/raw/master/202407051728271.png

```bash
netns delete aaa   # 删除aaa空间
# 删除后网卡也会消失
```

### 为多个命名空间配置网关使得网络互相联通

创建namespace1，namespace2命名空间

```bash
ip netns add namespace1
ip netns add namespace2
```

启动命名空间内的lo网卡设备

```bash
ip netns exec namespace1 ip link set dev lo up
ip netns exec namespace2 ip link set dev lo up
```

创建一对虚拟以太网接口（veth —> peer）设备

```bash
/usr/sbin/ip link add veth0 type veth peer name veth1
/usr/sbin/ip link add veth2 type veth peer name veth3
```

将对应的peer接口设备移入到对应的命名空间

```bash
ip link set veth1 netns namespace1
ip link set veth3 netns namespace2
```

配置IP地址（IP需要相互对应，一对设备应在同一个网段）

```bash
ifconfig veth0 5.5.5.1/24
ifconfig veth2 15.15.15.1/24
ip netns exec namespace1 ifconfig veth1 5.5.5.2/24
ip netns exec namespace2 ifconfig veth3 15.15.15.2/24
```

为命名空间内配置默认网关使其能够访问外部网络

由于命名空间内的网卡是peer接口，所以网关需要配置为与之对应的在物理机上的veth接口的IP地址

```bash
ip netns exec namespace1 route add default gw 5.5.5.1
ip netns exec namespace2 route add default gw 15.15.15.1
```

此时检查网络连通性，在命名空间一内使用ping命令访问命名空间二内设备的IP地址

```bash
ip netns exec namespace1 ping 15.15.15.2
```

验证命名空间内部网络可以互相通信