base镜像：

1. 不依赖与其他镜像，从scratch构建， FROM scratch
2. 其他镜像可以以其为基础进行扩展，通常是系统类镜像

计算机通常将数据分为两种 ——> 冷数据与热数据

冷数据/无状态数据（镜像内）———— 热数据/有状态数据（容器内）

/usr/local/apache2 /usr/local/apache2/htdocs

/usr/local/mysql /usr/local/mysql/data

### 构建镜像：

Dockerfile 是从上层到下层的顺序写的

Dockerfile中所有的执行命令都必须是base镜像内的命令

镜像构建的每一层都会切换目录

Dockerfile中切换格式，缓存不生效

Dockerfile可用参数：

FROM表示基于什么镜像构建

RUN表示在上层基础上执行指令（必须为全自动/非交互式）

CMD表示启动时默认执行的命令（多个CMD时，最上层的生效）

COPY表示复制文件到容器的路径中

ADD与COPY相同，但是可以指定解压缩路径

WORKDIR切换工作路径，以后每一层的运行命令都在此目录中

cd 切换只在当前层内生效

ENV设置变量，在以后的层可以被引用

Dockerfile文件内有两种格式：

shell格式：有shell的环境变量，比如$PATH，直接写命令就可以运行

exec格式：没有shell的环境变量，所有命令需要绝对路径（内部命令除外）

CMD与ENTRYPOINT的区别：

shell格式下：

ENTRYPOINT会运行，CMD不会运行

都可以识别以及调用ENV变量

exec格式下：

ENTRYPOINT一定会运行，CMD作为ENTRYPOINT的参数运行

CMD的命令会被docker run 的命令替代

\___结论：ENTRYPOINT写命令，CMD写参数

exec格式下不能直接读取变量

可用使用/bin/sh -c 启动shell并执行命令

结论：通常启动执行命令时需要使用exec格式，这样容器启动会使用更小的运行空间，如果shell格式则需要先加载shell启动再执行命令，则会占用更多资源

```bash
vim Dockerfile
###
FROM quay.io/rockylinux/rockylinux:9
RUN yum -y install net-tools 
RUN yum -y install httpd
RUN yum -y install procps-ng
CMD ["/bin/bash"]
###
docker build -t zxh_httpd:v1 ./    # 开始构建镜像，./为Dockerfile文件的相对路径
```

![https://gitee.com/zhaojiedong/img/raw/master/202407101515293.png](https://gitee.com/zhaojiedong/img/raw/master/202407101515293.png)

查询镜像历史

```bash
docker image history zxh_httpd:v1
```

![https://gitee.com/zhaojiedong/img/raw/master/202407101518161.png](https://gitee.com/zhaojiedong/img/raw/master/202407101518161.png)

构建v2版本镜像

导入nginx-1.24.0.tar.gz压缩包

```bash
vim Dockerfile
###
FROM quay.io/rockylinux/rockylinux:9
RUN yum -y install net-tools 
RUN yum -y install httpd
RUN yum -y install procps-ng
COPY README.txt /
ADD nginx-1.24.0.tar.gz /usr/src/
CMD ["/bin/bash"]
###
docker build -t zxh_httpd:v2 ./
```

开始构建后会使用之前构建产生的缓存

![https://gitee.com/zhaojiedong/img/raw/master/202407101523708.png](https://gitee.com/zhaojiedong/img/raw/master/202407101523708.png)

构建时不使用缓存(下载最新版软件)的方法：

1. 更改Dcokerfile文件内构建顺序
    
2. 指定构建容器时不使用缓存
    

```bash
docker build -t zxh_httpd:v3 ./ --no-cache
```

3. 使用命令清除缓存

```bash
docker buildx ls    # 查看缓存
docker buildx prune
```

### 实例：

Dockerfile：

```bash
FROM registry.cn-hangzhou.aliyuncs.com/zxh230/busybox:1.36
RUN touch runfile
RUN cd /usr/local/ && touch cdfile
COPY README.txt ./
WORKDIR /usr
RUN touch tmpfile
RUN /bin/sh -c "echo debug build image..."
```

![https://gitee.com/zhaojiedong/img/raw/master/202407101554601.png](https://gitee.com/zhaojiedong/img/raw/master/202407101554601.png)

原因：没有/usr/local目录

更改Dockerfile：

```bash
FROM registry.cn-hangzhou.aliyuncs.com/zxh230/busybox:1.36
RUN touch runfile
RUN cd /usr/sbin/ && touch cdfile
COPY README.txt ./
WORKDIR /usr
RUN touch tmpfile
RUN /bin/sh -c "debug build image..."
```

![https://gitee.com/zhaojiedong/img/raw/master/202407101610092.png](https://gitee.com/zhaojiedong/img/raw/master/202407101610092.png)

原因：/bin/bash命令格式错误

更改Dockerfile：

```bash
FROM registry.cn-hangzhou.aliyuncs.com/zxh230/busybox:1.36
RUN touch runfile
RUN cd /usr/sbin/ && touch cdfile
COPY README.txt ./
WORKDIR /usr
RUN touch tmpfile
RUN /bin/sh -c "echo debug build image..."
```

![https://gitee.com/zhaojiedong/img/raw/master/202407101611171.png](https://gitee.com/zhaojiedong/img/raw/master/202407101611171.png)