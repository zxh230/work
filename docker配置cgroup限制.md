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

```