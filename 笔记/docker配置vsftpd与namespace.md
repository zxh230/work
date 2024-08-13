配置 vsftpd
```shell
# 创建挂载目录
mkdir /nfs
# 启动容器rocky9
docker run -itd --name nfs --privileged --network host -v /nfs/:/nfs rocky:9 bash
# 配置nfs
docker exec -it nfs bash
yum -y install nfs-utils
rpcbind -w
/usr/sbin/rpc.nfsd 
/usr/sbin/rpc.mountd 
# 修改nfs配置文件
vi /etc/exports
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240813214313.png)

```shell
# 导出nfs配置
exportfs -ar
# 查看nfs配置
exportfs
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240813214407.png)
```shell
# 物理机验证
showmount -e 172.17.0.1
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240813214512.png)
```shell
# 挂载
mount -t nfs 172.17.0.1:/nfs /nfs
```

配置 namespace 命名空间，使其连通

```shell
ip netns add namespace1
ip netns add namespace2
ip netns exec namespace1 ip link set dev lo up
ip netns exec namespace2 ip link set dev lo up
/usr/sbin/ip link add veth0 type veth peer name veth1
/usr/sbin/ip link add veth2 type veth peer name veth3
ip link set veth1 netns namespace1
ip link set veth3 netns namespace2
ifconfig veth0 6.6.6.1/24
ifconfig veth2 16.16.16.1/24
ip netns exec namespace1 ifconfig veth1 6.6.6.2/24
ip netns exec namespace2 ifconfig veth3 16.16.16.2/24
ip netns exec namespace1 route add default gw 6.6.6.1
ip netns exec namespace2 route add default gw 16.16.16.1
# 验证
ip netns exec namespace1 ping 16.16.16.2
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240813214705.png)
