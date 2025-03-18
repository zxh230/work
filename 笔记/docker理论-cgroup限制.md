要求：

1、分配第 aa 容器使用一颗 CPU 分配第 bb 容器使用两颗 CPU

2、使用 cgroup 的方式: 挂起 cc 容器

3、分配 cc 容器的磁盘优先读写权重 100 写入数据到磁盘的频率为 90 MB/S

```shell
# 创建aa容器
docker run -itd --name aa --cpuset-cpus 1 busybox:1.36
# 查看cpu数量
cat /sys/fs/cgroup/system.slice/docker-f3acbe71f3e79be30f17802ec60a06d546761f9672894b580820fe97f085af7b.scope/cpuset.cpus
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814195603.png)

```shell
# 创建容器bb
docker run -itd --name bb --cpuset-cpus 2 busybox:1.36
# 查看cpu数量
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814195701.png)

```shell
# 创建容器cc
dockr run -it --name cc busybox:1.36
# 查询主磁盘
lsblk
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814200519.png)

```shell
# 查询设备号
ll /dev/nvme0n1
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814200624.png)

```shell
# 进入容器所对应的cgroup目录
docker ps
cd /sys/fs/cgroup/system.slice/docker-7773bfe1644d08cd15a87499eb0a3f822f08a47ebbad22570ef3d85008194b5f.scope/
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814200957.png)


```shell
# 开始进行读写限制
vim io.max
###
259:0 rbps=max wbps=94371840 riops=max wiops=max
###
# 写入权重配置
vim io.bfq.weight
###
default 100
###
# 开始测试
docker exec -it cc sh
time dd if=/dev/zero of=test.o bs=1M count=800 oflag=direct
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814201347.png)

```shell
# 挂起容器cc
# 进入容器的cgroup目录
cd /sys/fs/cgroup/system.slice/docker-7773bfe1644d08cd15a87499eb0a3f822f08a47ebbad22570ef3d85008194b5f.scope/
# 更改cgroup.freeze文件，将0改为1
# 尝试进入容器
docker exec -it cc sh
# 无法进入
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814201612.png)

```shell
# 重新改为0后尝试再次进入容器
docker exec -it cc sh
# 此时可以进入
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240814201729.png)
