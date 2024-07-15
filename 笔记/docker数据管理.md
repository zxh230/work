# docker数据管理

==docker 的数据管理==
关于volume(卷)的权限：selinux权限（仅限于redhed系统）RO，RW权限（本地权限）
挂载：bind mount — > 将宿主机目录挂载到容器
			managed volume(将容器数据保存到宿主机) —>  将容器内目录挂载到宿主机
			tmpfs —>  将目录挂载到内存

==只能挂载目录或文件==

## tmpfs:

```shell
# 将目录/app挂载到内存中，/app目录会自动创建
docker run -itd --name tamtest --mount type=tmpfs,destination=/app busybox:1.36
# 查看挂载信息
docker inspect [容器id]
```

|![image-20240715140301570](https://gitee.com/zhaojiedong/img/raw/master/image-20240715140301570.png)

## bind mount:

```shell
mkdir /htdocs
echo the web server by zxh > /htdocs/index.html
# 以--mount方式挂载到nginx
docker run -itd --name devtest --mount type=bind,source=/htdocs,target=/usr/share/nginx/html nginx:1.24 
# 以-v方式挂载到htpd
docker run -itd --name devtest1 -v /htdocs/:/usr/local/apache2/htdocs httpd:latest
```

### 查看挂载信息

nginx：
|![image-20240715141428390](https://gitee.com/zhaojiedong/img/raw/master/image-20240715141428390.png)

httpd:
|![image-20240715141506874](https://gitee.com/zhaojiedong/img/raw/master/image-20240715141506874.png)
==当宿主机源文件改变时，容器内相应的文件也会发生变化==

```shell
echo 
```

|![image-20240715141649729](https://gitee.com/zhaojiedong/img/raw/master/image-20240715141649729.png)

==此时容器内修改文件宿主机也会发生变化==
修改权限使得容器内挂载只读

```shell
# 将目录以只读的方式挂载到容器内
docker run -itd --name devtest -v /htdocs/:/usr/local/apache2/htdocs:ro httpd:latest
# 查看挂载信息
docker inspect devtest
```

|![image-20240715141956777](https://gitee.com/zhaojiedong/img/raw/master/image-20240715141956777.png)

此时权限变为ro（只读）

### Propagation数据传播

shard

### 互斥权限 —> selinux权限

```shell
docker run -itd --name devtest1 -v /htdocs/:/usr/local/apache2/htdocs:ro httpd:latest
# 验证写入权限
```

|![image-20240715144100657](https://gitee.com/zhaojiedong/img/raw/master/image-20240715144100657.png)



关于selinux标签在volume中的使用：
不能使用–mount设置selinux标签，设置selinux

```shell
docker run -itd --name devweb -v /htdocs/:/usr/share/nginx/html:Z nginx:1.24 
```

|![image-20240715144519417](https://gitee.com/zhaojiedong/img/raw/master/image-20240715144519417.png)

> selinux标签已经生效，但是没有作用

------

## managed volume：
违规用法（直接挂载，不进行创建卷的操作）：

```shell
docker run -itd --name aaa -v /usr/share/nginx/html nginx:1.24
```

正常用法（先创建卷在进行挂载）：

```shell
# 创建一个卷
docker volume create apache-index
docker volume ls
```

|![image-20240715145443490](https://gitee.com/zhaojiedong/img/raw/master/image-20240715145443490.png)

新创建的卷内没有文件

|![image-20240715145530956](https://gitee.com/zhaojiedong/img/raw/master/image-20240715145530956.png)

```shell
# 然后进行挂载
docker run -itd --name aaa -v apache-index:/usr/share/apache2/htdocs httpd:latest 
# 查看详细信息
```

![image-20240715145901601](https://gitee.com/zhaojiedong/img/raw/master/image-20240715145901601.png)
挂载的类型为 volume

------

## 删除卷：
docker volume rm (当卷在被使用时不能被删除)
docker volume prune (删除无主的卷，自主创建的卷默认有主，不会删除)

------

## 将文件拷贝到容器中：

```shell
# 将当前目录的shart.sh脚本拷贝到容器的/usr目录下
docker cp ./start.sh bbb:/usr
# 验证
docker exec -it bbb ls /usr/
```

![image-20240715150535368](https://gitee.com/zhaojiedong/img/raw/master/image-20240715150535368.png)

-------

## 将文件挂载到容器内：

```shell
docker run -itd --name aaa -v /htdocs/index.html:/usr/share/nginx/html/aaa.html nginx:1.24
```

![image-20240715151001119](https://gitee.com/zhaojiedong/img/raw/master/image-20240715151001119.png)

------

##  共享volume：
volume container —> 专门为其他容器提供volume的容器
volume nfs(samba,nfs) —> 挂载后端服务
	插件共享：sshFS
data-packed volume container —> 数据放到镜像中后随便迁移

### 创建集群

```shell
docker create --name vc_data --volume /htdocs/:/usr/local/apache2/htdocs --volume /usr/local/apache2/logs busybox:1.36 
```

![image-20240715155200153](https://gitee.com/zhaojiedong/img/raw/master/image-20240715155200153.png)

```shell
# 将卷容器挂载到容器
docker run --name web1 -itd -d -p 8081:80 --volumes-from vc_data httpd:latest
docker run --name web2 -itd -d -p 8082:80 --volumes-from vc_data httpd:latest
docker run --name web3 -itd -d -p 8083:80 --volumes-from vc_data httpd:latest
# 验证
curl 10.15.200.241:8081
curl 10.15.200.241:8082
curl 10.15.200.241:8083
```

|![image-20240715155342476](https://gitee.com/zhaojiedong/img/raw/master/image-20240715155342476.png)

### volume连接外部存储

```shell
# 两台虚拟机安装nfs
yum -yq install nfs-utils
```

docker02：
```shell
# 创建挂载目录
mkdir /nfsdata
# 修改nfs配置文件
vim /etc/exports
###
/nfsdata *(rw,sync,no_root_squash)
###
# 重启nfs-server
exportfs -r
systemctl restart nfs-server
```

docker01：
```shell
systemctl restart nfs-server
# 查看可挂载点
showmount -e 10.15.200.242
```

|![image-20240715161028998](https://gitee.com/zhaojiedong/img/raw/master/image-20240715161028998.png)

```shell
# 创建nfs卷容器
docker volume create --driver local --opt type=nfs --opt o=addr=10.15.200.242,rw --opt device=:/nfsdata volume-nfs
# 挂载nfs卷容器
docker run -itd --name box1 --volume volume-nfs:/nfs busybox:1.36
# 验证
docker exec -it box1 sh
echo hello > /nfsdata/aaa.o
# 在docker02上查看
```

|![image-20240715161707967](https://gitee.com/zhaojiedong/img/raw/master/image-20240715161707967.png)

------

#### docker安装插件

```shell
docker plugin install --grant-all-permissions vieux/sshfs
```

------

### 数据包卷容器

将数据放入镜像 —>  将镜像做成容器 —> 

```shell
# 创建Dockerfile
vim Dockerfile
###
FROM busybox:1.36
ADD htdocs /usr/local/apache2/htdocs
VOLUME /usr/local/apache2/htdocs
###
# 在当前位置创建目录
mkdir htdocs
# 开始构建镜像
docker build -t datapack ./
# 创建卷容器
docker create --name vc_data datapack
# 启动httpd:latest容器，将端口80映射到宿主机上的80端口，并且使用vc_data卷容器
docker run -d -p 80:80 --volumes-from vc_data httpd:latest
# 查看挂载信息
docker inspect vc_data 
```

![image-20240715163615890](https://gitee.com/zhaojiedong/img/raw/master/image-20240715163615890.png)

```shell
# 查看对应的卷容器信息
docker volume inspect a1f50225d034fb19f1d9291ec0748d8488ebe2315ee2508e7fe7b6f0ca3c1c90
```

![image-20240715163917589](https://gitee.com/zhaojiedong/img/raw/master/image-20240715163917589.png)

```shell
cd /var/lib/docker/volumes/a1f50225d034fb19f1d9291ec0748d8488ebe2315ee2508e7fe7b6f0ca3c1c90/_data
echo hello world > index.html
curl 172.17.0.3
```

|![image-20240715163935179](https://gitee.com/zhaojiedong/img/raw/master/image-20240715163935179.png)

------

## prometheuse的基础组件

cadvisor：采集容器的日志信息
node-exproter：采集宿主机的相关信息
grafana：UI界面

prometheuse：是服务端





[‘10.15.200.241:9090’,’10.15.200.241:8080’,10.15.200.241:9100],’10.15.200.241:’

```shell
```

==dewde==

_dewde_

*cdwwwcd*

- 

### dwdgwe