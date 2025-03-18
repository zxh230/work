![0da18825bc0c5e8d8f04736cfd78f94.jpg](https://gitee.com/zhaojiedong/img/raw/master/0da18825bc0c5e8d8f04736cfd78f94.jpg )

docker的image存储

1，/var/lib/docker/overlay2 存储镜像的每一层具体的数据

```bash
# 查找镜像quay.io/rockylinux/rockylinux:9的数据目录
docker image inspect quay.io/rockylinux/rockylinux:9
```

![https://gitee.com/zhaojiedong/img/raw/master/202407091607707.png](https://gitee.com/zhaojiedong/img/raw/master/202407091607707.png)

2，/var/lib/docker/image
      |—  /imagedb  镜像的源文件（也是镜像的所需层）
      |—  /layerdb  镜像分层关系（parent记录上层镜像）

******
容器层：

COW（Copy-On-Write, COW）写实复制

快照的一瞬数据的变化量，存储到快照空间内，（增删改查）

联合挂载：

```bash
mkdir upper
mkdir lower
mkdir merged
mkdir work
echo "im from lower" > lower/in_lower.txt
echo "im from upper" > upper/in_upper.txt
echo "im both,im from lower" > lower/in_both.txt
echo "im both,im from upper" > upper/in_both.txt
mount (-t overlay类型) （overlay设备名） -o lowerdir=./lower,upperdir=./upper,workdir=./work ./merged
```

bootfs：开机引导程序

rootfs：所有容器的集合