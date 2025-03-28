==要求==
1 创建docker网卡 ip 地址为: 172.86.86.0/24
2 创建三个容器: nginx 容器 \ php 容器 \ mysql 容器 链接到该网络
访问宿主机的端口 8080, 即可访问 php 的测试页面及 mysql 链接测试

- nginx容器使用之前创建好的nginx:1.24镜像
- mysql同理
- php手动创建

## 创建网卡

```shell
# 网卡名docker 网段为172.86.86.0 网关为172.86.86.1
docker network create --driver bridge --subnet 172.86.86.0/24 --gateway 172.86.86.1 docker
```

## 创建php镜像

下载php所需文件：>[php构建](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/php%E6%9E%84%E5%BB%BA.zip)

```shell
# windows上即将php构建.7z解压，将解压后文件导入
mkdir 7_12lnmp/
mv www.conf php-8.2.7.tar.gz index.php 7_12lnmp/
cd 7_12lnmp/
# 创建Dockerfile文件
vim Dockerfile
### FROM更改为自己的rockylinux9镜像+版本
FROM registry.cn-hangzhou.aliyuncs.com/zxh230/rockylinux:9
ADD php-8.2.7.tar.gz /
RUN yum -y install make vim iproute gcc openssl-devel zlib-devel pcre-devel sqlite-devel libxml2-devel bzip2-devel libcurl-devel freetype-devel
RUN cd /php-8.2.7/ && ./configure --prefix=/usr/local/php  --with-pdo-mysql  --with-openssl --with-freetype --with-jpeg --with-zlib --with-bz2 --enable-fpm --enable-sockets --enable-sysvshm --enable-mysqlnd --enable-xml --with-mysqli && make -j 6 && make install
RUN yes | cp -r /php-8.2.7/sapi/fpm/* /usr/local/php/etc/
RUN rm -rf /usr/local/php/etc/php-fpm.d/www.conf.default
COPY www.conf /usr/local/php/etc/php-fpm.d/
RUN mkdir -p /usr/local/nginx/html/
COPY index.php /usr/local/nginx/html/index.php
CMD ["/bin/bash"]
###
# 创建index.php文件
vim index.php
###
<?php
  $link = mysqli_connect('172.86.86.4','root','123.com');
  if($link) {
    echo  "非常开心, 数据库连接成功!!!\n";
  }
  else {
    echo  "恭喜恭喜, 数据库连接失败~~~\n";
  };
?>
###
# 开始构建镜像
docker build -t php:8 ./
# 构建完成后启动镜像，分配网卡与IP地址，使其持久化
docker run -itd --network docker --ip 172.86.86.3 --restart always --name php php:8
docker exec -it php /usr/local/php/sbin/php-fpm
# 查看容器
docker ps
# 验证php是否启动
docker exec -it php ss -tulanp |grep php
```

![image-20240712224903115](https://gitee.com/zhaojiedong/img/raw/master/image-20240712224903115.png)

## 编辑nginx镜像|

检查之前构建的nginx0710:v1.0是否还在
如果不在>[跳转网页](https://gitee.com/zhaojiedong/work/blob/master/笔记/构建nginx镜像.md)

```shell
# 启动之前构建的nginx镜像
docker run -itd --network docker --ip 172.86.86.2 -p 8080:80 --name web nginx0710:v1.0
# 进入容器web并修改配置
docker exec -it web bash
vi /usr/local/nginx/conf/nginx.conf
### 修改部分
location ~ \.php$ {
    root           html;
    fastcgi_pass   172.86.86.3:9000;
    fastcgi_index  index.php;
    fastcgi_param  SCRIPT_FILENAME  /usr/local/nginx/html/index.php;
    include        fastcgi_params;
}
###
```

|![image-20240712225334008](https://gitee.com/zhaojiedong/img/raw/master/image-20240712225334008.png)

```shell
# 创建index.php网页文件
vi /usr/local/nginx/html/index.php
###
<?php
  $link = mysqli_connect('172.86.86.4','root','123.com');
  if($link) {
    echo  "非常开心, 数据库连接成功!!!\n";
  }
  else {
    echo  "恭喜恭喜, 数据库连接失败~~~\n";
  };
?>
###
# 重载nginx
nginx -s reload
# 退出容器
exit
# 查看nginx服务是否正常
curl 172.86.86.2
```

|![image-20240712225721494](https://gitee.com/zhaojiedong/img/raw/master/image-20240712225721494.png)

## 构建mysql镜像

mysql软件包下载：>
夸克网盘：https://pan.quark.cn/s/01fdbb96d2d6
提取码：U9uU

```shell
mkdir 7_12lnmp/mysql
cd !$
mv /root/mysql-8.0.38-linux-glibc2.28-x86_64.tar.xz ./
vim Dockerfile
### 自行更换FROM中的镜像，确保是rocky9即可
FROM rockylinux:9
COPY mysql-8.0.38-linux-glibc2.28-x86_64.tar.xz /root
RUN dnf -y install xz perl-JSON perl-Data-Dumper libaio numactl
RUN tar -xf /root/mysql-8.0.38-linux-glibc2.28-x86_64.tar.xz -C /usr/local/
RUN mv /usr/local/mysql-8.0.38-linux-glibc2.28-x86_64 /usr/local/mysql
RUN useradd mysql
RUN mkdir /var/lib/mysql \
    && chown -R mysql:mysql /var/lib/mysql
RUN mkdir /var/run/mysqld \
    && chown -R mysql:mysql /var/run/mysqld
RUN mkdir /var/log/mysql \
    && chown -R mysql:mysql /var/log/mysql
RUN ln -s /usr/local/mysql/bin/* /usr/local/bin/
EXPOSE 3306
ENTRYPOINT ["/bin/bash"]
###
# 开始构建镜像,确保没有重名镜像
docker build -t mysql:8 ./
# mysql镜像实例化，启动mysql服务并授权
docker run -itd --name mysql --network docker --ip 172.86.86.4 --restart always mysql:8
docker exec -itd mysql /usr/local/mysql/bin/mysqld --initialize-insecure  --user=mysql
docker exec -itd mysql /usr/local/mysql/bin/mysqld --user=mysql
# 进入数据库授权，无密码回车即可
docker exec -it mysql mysql -uroot -p
create user 'root'@'172.86.86.%' identified by '123.com';
grant all on *.* to 'root'@'172.86.86.%';
# 退出数据库，验证访问结果,10.15.200.241为本机IP
exit
curl 10.15.200.241:8080/index.php
```

|![image-20240712232246566](https://gitee.com/zhaojiedong/img/raw/master/image-20240712232246566.png)