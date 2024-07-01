## nginx转发php实现负载均衡MMM数据库与动静分离

------

- ### nginx转发php实现负载均衡

  1. 配置MMM数据库集群（==node03，node04，node05==）

     解压Percona-XtraDB-Cluster.el9.tgz

     ```shell
     tar -xf Percona-XtraDB-Cluster.el9.tgz
     ```

     配置yum仓库

     ```shell
     echo "[AappStream]
     name=AappStream
     baseurl=file:///root/Percona-XtraDB-Cluster/
     gpgcheck=0
     enabled=1" >> /etc/yum.repos.d/rocky9.repo
     ```

     创建证书目录，移动证书

     ```shell
     tar -xf certs.tgz
     mkdir /etc/db_certs/
     mv certs/* /etc/db_certs/
     chown mysql:mysql /etc/db_certs/ -R
     ```

     修改my.cnf配置文件

     ```shell
     vim /etc/my.cnf
     [client]
     socket=/var/lib/mysql/mysql.sock
     ssl-ca=/etc/db_certs/ca.pem
     ssl-cert=/etc/db_certs/server-cert.pem
     ssl-key=/etc/db_certs/server-key.pem
     [mysqld]
     server-id=103 # 节点唯一id
     datadir=/var/lib/mysql
     socket=/var/lib/mysql/mysql.sock
     log-error=/var/log/mysqld.log
     pid-file=/var/run/mysqld/mysqld.pid
     binlog_expire_logs_seconds=604800
     wsrep_provider=/usr/lib64/galera4/libgalera_smm.so
     wsrep_cluster_address=gcomm://10.15.200.103,10.15.200.104,10.15.200.105
     # 集群内所有主机
     binlog_format=ROW
     wsrep_slave_threads=8
     wsrep_log_conflicts
     innodb_autoinc_lock_mode=2
     wsrep_node_address=10.15.200.103 # 本机IP地址
     wsrep_node_name=node03 # 本机主机名，唯一
     wsrep_cluster_name=zhaojiedong-exam # 集群名，所有主机相同
     pxc_strict_mode=ENFORCING
     wsrep_sst_method=xtrabackup-v2
     wsrep_provider_options="socket.ssl=yes;socket.ssl_ca=/etc/db_certs/ca.pem;socket.ssl_cert=/etc/db_certs/server-cert.pem;socket.ssl_key=/etc/db_certs/server-key.pem"
     ssl-ca=/etc/db_certs/ca.pem
     ssl-cert=/etc/db_certs/server-cert.pem
     ssl-key=/etc/db_certs/server-key.pem
     [sst]
     encrypt=4
     ssl-ca=/etc/db_certs/ca.pem
     ssl-cert=/etc/db_certs/server-cert.pem
     ssl-key=/etc/db_certs/server-key.pem
     ```

     node04,node05同理

     启动数据库，修改密码

     ```shell
     # node03启动数据库
     systemctl start mysql@bootstrap.service
     # 在node03上查看随机密码
     grep 'temporary password' /var/log/mysqld.log | awk -F'[@]' '{print $2}' | awk -F':' '{print $2}'
     # 进入mysql并更改密码
     ALTER USER 'root'@'localhost' IDENTIFIED BY 'rootPass'
     # node04,node05启动数据库
     systemctl start mysql
     # 创建数据库[zhaojiedong]
     mysql -uroot -prootPass -e"create database zhaojiedong;"
     # 无视Warning警告
     # 在库中创建表
     mysql -uroot -prootPass
     use zhaojiedong;
     CREATE TABLE uuid (zhaojiedong INT AUTO_INCREMENT PRIMARY KEY,赵杰栋 VARCHAR(36));
     # 创建用户并授权
     CREATE USER 'zhaojiedong'@'10.15.200.%' IDENTIFIED BY 'rootPass';
     GRANT ALL PRIVILEGES ON *.* TO 'zhaojiedong'@'10.15.200.%' WITH GRANT OPTION;
     ```

  2. 配置nginx负载均衡，转发3306端口（==ha01，ha02，配置完全一样==）

     安装keepalived并配置

     ```shell
     yum -yq install keepalived
     # ha01
     yum -yq install keepalived
     echo "global_defs {
         router_id ha01.example.cn
     }
     vrrp_instance node_http {
         state MASTER
         interface ens160
         virtual_router_id 116
         priority 116
         advert_int 1
         authentication {
             auth_type PASS
             auth_pass ha0102
         }
         virtual_ipaddress {
             10.15.200.116
             10.15.200.117
         }
     }" > /etc/keepalived/keepalived.conf
     
     # ha02
     yum -yq install keepalived
     echo "global_defs {
         router_id ha02.example.cn
     }
     vrrp_instance node_http {
         state BACKUP
         interface ens160
         virtual_router_id 116
         priority 100
         advert_int 1
         authentication {
             auth_type PASS
             auth_pass ha0102
         }
         virtual_ipaddress {
             10.15.200.116
             10.15.200.117
         }
     }" > /etc/keepalived/keepalived.conf
     # 俱启动keepalived
     systemctl start keepalived
     ```

     源码安装nginx

     ```shell
     yum -yq install gcc zlib-devel pcre-devel
     tar -xf nginx-1.26.0.tar.gz
     cd nginx-1.26.0/
     ./configure --prefix=/usr/local/nginx --conf-path=/etc/nginx/nginx.conf --user=nginx --group=nginx --with-stream --sbin-path=/usr/sbin/nginx
     make ; make install
     useradd nginx
     ```

     配置nginx

     在nginx.conf中添加

     ```shell
     include       /etc/nginx/conf.d/db_proxy.conf;	# 在http模块上方添加
     include       /etc/nginx/conf.d/front.conf;	# 在http模块内添加
     ```

     ![image-20240531160006406](https://gitee.com/zhaojiedong/img/raw/master/202405311600485.png)

     增加日志格式并指定日志文件位置

     ```shell
     log_format  proxy '$remote_addr - $remote_user [$time_local] "$request" '
                       '$status $body_bytes_sent "$http_referer" '
                       '"$http_user_agent" "$http_x_forwarded_for"';
     access_log  /dev/shm/db_pxc.log  proxy;
     ```

     ![image-20240531160156939](https://gitee.com/zhaojiedong/img/raw/master/202405311601972.png)

     创建目录，写入配置文件

     ```shell
     mkdir /etc/nginx/conf.d/
     vim /etc/nginx/conf.d/db_proxy.conf
     stream {
         upstream mysql_nodes {
            	 server 10.15.200.103:3306 weight=1 max_fails=3 fail_timeout=30s;
        		 server 10.15.200.104:3306 weight=1 max_fails=3 fail_timeout=30s;
        		 server 10.15.200.105:3306 weight=1 max_fails=3 fail_timeout=30s;
     	}
     
     	server {
             listen 3306;
             proxy_pass mysql_nodes;
         }
     }
     ```

     启动nginx

     ```shell
     nginx -t
     nginx
     ```

  3. 配置php+nginx（==node01==）

     源码安装nginx

     ```shell
     yum -yq install gcc zlib-devel pcre-devel
     tar -xf nginx-1.26.0.tar.gz
     cd nginx-1.26.0/
     ./configure --prefix=/usr/local/nginx --conf-path=/etc/nginx/nginx.conf --user=nginx --group=nginx --sbin-path=/usr/sbin/nginx
     make ; make install
     useradd nginx
     ```

     配置nginx使其支持php

     ```shell
     # 查看php监听位置
     grep "listen =" /etc/php-fpm.d/www.conf
     # 输出listen = /run/php-fpm/www.sock
     vim /etc/nginx/nginx.conf
     # 添加
     location ~ \.php$ {
             root           html;
             fastcgi_pass   unix:/run/php-fpm/www.sock;
             # 改为php监听位置，unix为套接字
             fastcgi_index  index.php;
             fastcgi_param  SCRIPT_FILENAME  /usr/local/nginx/html$fastcgi_script_name;
             include        fastcgi_params;
             }
     ```

     安装php及其扩展

     ```shell
     yum -yq install php php-mysqlnd php-mysqli
     ```

     写入php网页文件

     ```shell
     vim /usr/local/nginx/html/zhaojiedong_db.php
     ```

     ```php
     <?php
       $link = mysqli_connect('pxe.example.cn','zhaojiedong','rootPass','zhaojiedong');
       if($link) {
         $uuid=exec('uuidgen');
         $sql = "INSERT INTO uuid (赵杰栋) VALUES ('$uuid')";
         if (mysqli_query($link, $sql)) {
             echo "数据写入成功";
             echo PHP_EOL;
             echo $uuid;
             echo PHP_EOL;
         } else {
             echo "Error: " . $sql . "<br>" . mysqli_error($link);
         }
       }
       else {
         echo "恭喜恭喜, 数据库连接失败~~~";
         echo PHP_EOL;
       };
     ?>
     ```

     写入域名解析

     ```shell
     echo 10.15.200.116 pxe.example.cn >> /etc/hosts
     ```

     启动php与nginx进行测试

     ```shell
     systemctl start php-fpm
     nginx -t
     nginx
     ```

  4. 小地球写入域名解析

     pxe.example.cn  ------  10.15.200.101

  5. 浏览器访问pxe.example.cn/zhaojiedong_db.php进行测试

------

------

- nginx实现动静分离（其一：超链接）

  在ha01，ha02上写入虚拟主机配置文件

  ```shell
  vim /etc/nginx/conf.d/front.conf
  server {
  	server_name zhaojiedong.example.cn;
  	listen 80;
  	root /nginx;
  }
  ```

  网页文件实例：

  [/nginx/static/index.html](https://gitee.com/zhaojiedong/img/blob/master/文件/index(超链接static).html)，局部图：

  ![image-20240531164156367](https://gitee.com/zhaojiedong/img/raw/master/202405311641416.png)

  [/nginx/valid/index.html](https://gitee.com/zhaojiedong/img/blob/master/文件/index(超链接valid).html))，局部图：

  ![image-20240531165057134](https://gitee.com/zhaojiedong/img/raw/master/202405311650165.png)

  /nginx/html：

  ```html
  <html>
  <h1 align="center" style="color:red ; font-size:40px">default index by: zhaojiedong</h1>
  </html>
  ```

  文件结构如下：![image-20240531165424063](https://gitee.com/zhaojiedong/img/raw/master/202405311654088.png)

  配置图片服务器，node02

  yum本地安装nginx

  配置nginx，释放main日志格式与日志创建条目

  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
  access_log   /dev/shm/static_access.log  main;

  在nginx.conf中添加

  ```shell
  include       /etc/nginx/conf.d/front.conf;	# 在http模块内添加
  ```

  修改配置文件

  ```shell
  vim /etc/nginx/conf.d/front.conf
  server {
      server_name static.example.cn;
      listen 80;
      root /nginx/;
  
      access_log  /dev/shm/static_access.log;
      error_log  /dev/shm/static_error.log;
      
  }
  ```

  解压图片压缩包[nginx_img.tgz](https://gitee.com/zhaojiedong/img/raw/master/%E6%96%87%E4%BB%B6/nginx_img.tgz)

  ```shell
  tar -xf nginx_img.tgz -C /
  ```

  目录结构：![image-20240531170229026](https://gitee.com/zhaojiedong/img/raw/master/202405311702062.png)

  ------

- nginx实现动静分离（其二：反向代理）

  在ha01，ha02上写入反向代理配置文件

  ```shell
  vim /etc/nginx/conf.d/front.conf
  upstream zhaojiedong {
      server 10.15.200.102:80;
  }
  
  server {
      server_name zhaojiedong.example.cn;
      listen 80;
      root /nginx/;
  
      location /static/6ecc/ {
      proxy_pass http://zhaojiedong;
      proxy_set_header Host static.example.cn;
      }
      location /valid/dt/ {
      proxy_pass http://zhaojiedong;
      proxy_set_header Host static.example.cn;
      }
  }
  ```

  在node02上写入配置文件：

  ```shell
  vim /etc/nginx/conf.d/front.conf
  server {
      server_name static.example.cn;
    listen 80;
      root /nginx/;

      access_log  /dev/shm/static_access.log;
      error_log  /dev/shm/static_error.log;
      
    location /static/6ecc/ {
      root /nginx/;
    }
      location /valid/dt/ {
      root /nginx/;
      }
  }
  ```
  
  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
  access_log   /dev/shm/static_access.log  main;
  
  在nginx.conf中添加
  
  ```shell
  include       /etc/nginx/conf.d/front.conf;	# 在http模块内添加
  ```
  
  网页文件实例：

  [/static/index.html](https://gitee.com/zhaojiedong/img/blob/master/文件/index(反向代理static).html)如图：

  ![2](https://gitee.com/zhaojiedong/img/raw/master/202405311749759.png)

  [/nginx/valid/index.html](https://gitee.com/zhaojiedong/img/blob/master/文件/index(反向代理valid).html)如图：

  ![image-20240531175843580](https://gitee.com/zhaojiedong/img/raw/master/202405311758622.png)

  /nginx/html：

  ```html
<html>
  <h1 align="center" style="color:red ; font-size:40px">default index by: zhaojiedong</h1>
  </html>
  ```
  
  文件结构如下：![image-20240531165424063](https://gitee.com/zhaojiedong/img/raw/master/202405311654088.png)

  配置图片服务器，node02

  yum本地安装nginx

  修改配置文件

  ```shell
vim /etc/nginx/conf.d/front.conf
  server {
      server_name static.example.cn;
      listen 80;
      root /nginx/;
  
      access_log  /dev/shm/static_access.log;
      error_log  /dev/shm/static_error.log;
      
      location /static/6ecc/ {
      root /nginx/;
      }
      location /valid/dt/ {
      root /nginx/;
      }
  }
  ```
  
  解压图片压缩包[nginx_img.tgz](https://gitee.com/zhaojiedong/img/raw/master/%E6%96%87%E4%BB%B6/nginx_img.tgz)

  ```shell
tar -xf nginx_img.tgz -C /
  ```
  
  目录结构：![image-20240531170229026](https://gitee.com/zhaojiedong/img/raw/master/202405311702062.png)

  ------

- nginx实现动静分离（其三：location）

   在ha01，ha02上写入配置文件

  ```shell
  vim /etc/nginx/conf.d/front.conf
  server {
      server_name zhaojiedong.example.cn;
      listen 80;
      root /nginx/;
  
      location /static/6ecc/ {
      proxy_pass http://static.example.cn;
      }
      location /valid/dt/ {
      proxy_pass http://static.example.cn;
      }
  }
  ```

  在node02上写入配置文件：

  ```shell
  vim /etc/nginx/conf.d/front.conf
  server {
      server_name static.example.cn;
      listen 80;
      root /nginx/;
  
      access_log  /dev/shm/static_access.log;
      error_log  /dev/shm/static_error.log;
      
      location /static/6ecc/ {
      root /nginx/;
      }
      location /valid/dt/ {
      root /nginx/;
      }
  }
  ```
  
  配置nginx，释放main日志格式与日志创建条目
  
  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
  access_log   /dev/shm/static_access.log  main;
  
  在nginx.conf中添加
  
  ```shell
  include       /etc/nginx/conf.d/front.conf;	# 在http模块内添加
  ```

  网页文件实例：

  [/static/index.html](https://gitee.com/zhaojiedong/img/blob/master/文件/index(反向代理static).html)如图：

  ![2](https://gitee.com/zhaojiedong/img/raw/master/202405311749759.png)

  [/nginx/valid/index.html](https://gitee.com/zhaojiedong/img/blob/master/文件/index(反向代理valid).html)如图：

  ![image-20240531175843580](https://gitee.com/zhaojiedong/img/raw/master/202405311758622.png)

  /nginx/html：

  ```html
  <html>
  <h1 align="center" style="color:red ; font-size:40px">default index by: zhaojiedong</h1>
  </html>
  ```

  文件结构如下：![image-20240531165424063](https://gitee.com/zhaojiedong/img/raw/master/202405311654088.png)

  配置图片服务器，node02

  yum本地安装nginx

  修改配置文件

  ```shell
  vim /etc/nginx/conf.d/front.conf
  server {
      server_name static.example.cn;
      listen 80;
      root /nginx/;
  
      access_log  /dev/shm/static_access.log;
      error_log  /dev/shm/static_error.log;
  }
  ```

  解压图片压缩包[nginx_img.tgz](https://gitee.com/zhaojiedong/img/raw/master/%E6%96%87%E4%BB%B6/nginx_img.tgz)

  ```shell
  tar -xf nginx_img.tgz -C /
  ```

  目录结构：![image-20240531170229026](https://gitee.com/zhaojiedong/img/raw/master/202405311702062.png)

  写入域名解析

  ```shell
  echo 10.15.200.102 static.example.cn >> /etc/hosts
  ```

  