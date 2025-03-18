------

源码安装LNMP环境

安装前置依赖

```shell
yum install gcc openssl-devel zlib-devel pcre-devel sqlite-devel libxml2-devel bzip2-devel libcurl-devel freetype-devel -y
```

#### nginx

导入nginx-1.26.0压缩包

解压

```shell
tar -xf nginx-1.26.0*
cd nginx*
./configure --prefix=/usr/local/nginx --user=nginx --group=nginx --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf
make ; make install
useradd nginx
echo hello nginx! >> /usr/local/nginx/html/index.html
nginx
```

#### php

导入php-8.2.7.tar.gz压缩包

```shell
tar -xf php-8.2.7.tar.gz
cd php-8.2.7/
./configure --prefix=/usr/local/php --with-pdo-mysql --with-openssl --with-freetype --with-jpeg --with-zlib --with-bz2 --with-curl --with-mhash --enable-fpm --enable-sockets --enable-sysvshm --enable-mysqlnd --enable-xml
make
make install
cp /usr/local/php/etc/php-fpm.conf.default /usr/local/php/etc/php-fpm.conf
cp /usr/local/php/etc/php-fpm.d/www.conf.default /usr/local/php/etc/php-fpm.d/www.conf
vim /usr/local/php/etc/php-fpm.d/www.conf
```

更改启动用户

![image-20240528100943854](https://gitee.com/zhaojiedong/img/raw/master/202405281010236.png)

更改nginx的启动用户

![image-20240528101235182](https://gitee.com/zhaojiedong/img/raw/master/202405281012211.png)

更改nginx默认php搜索路径

![image-20240528101331314](https://gitee.com/zhaojiedong/img/raw/master/202405281013337.png)

$document_root为nginx内置变量，指向默认网页文件目录

写入测试php网页文件

```shell
cat /usr/loacl/nginx/html/phpinfo.php << "EOF"
<?php
phpinfo();
?>
EOF
```

重载并测试

```shell
nginx -s reload
curl 127.0.0.1/phpinfo.php
```

