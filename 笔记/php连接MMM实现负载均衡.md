------

#### MMM

1. 将压缩包导入虚拟机并解压Percona-XtraDB-Cluster.el9.tgz

2. 配置yum仓库

   ```shell
   echo "[AappStream]
   name=AappStream
   baseurl=file:///root/Percona-XtraDB-Cluster/
   gpgcheck=0
   enabled=1" >> /etc/yum.repos.d/rocky9.repo
   ```

3. 安装软件包

   ```shell
   yum -y install percona-xtradb-cluster
   ```

4. 配置hosts解析

   ```shell
   echo "10.15.200.101 node01.example.cn node01
   10.15.200.102 node02.example.cn node02
   10.15.200.103 node03.example.cn node03" >> /etc/hosts
   ```

5. 解压certs.tgz并移动到/etc/mysql/下

   ```shell
   tar -xf certs.tgz
   mkdir -p /etc/mysql/
   mv certs/ /etc/mysql/
   chown mysql:mysql /etc/mysql/certs/ -R
   ```

6. 修改配置文件(注#需要改变)

   ```shell
   vim /etc/my.cnf
   [client]
   socket=/var/lib/mysql/mysql.sock
   ssl-ca=/etc/mysql/certs/ca.pem
   ssl-cert=/etc/mysql/certs/server-cert.pem
   ssl-key=/etc/mysql/certs/server-key.pem
   [mysqld]
   server-id=101 # 每台唯一id
   datadir=/var/lib/mysql
   socket=/var/lib/mysql/mysql.sock
   log-error=/var/log/mysqld.log
   pid-file=/var/run/mysqld/mysqld.pid
   binlog_expire_logs_seconds=604800
   wsrep_provider=/usr/lib64/galera4/libgalera_smm.so
   wsrep_cluster_address=gcomm://10.15.200.101,10.15.200.102,10.15.200.103
   # 集群内所有主机
   binlog_format=ROW
   wsrep_slave_threads=8
   wsrep_log_conflicts
   innodb_autoinc_lock_mode=2
   wsrep_node_address=10.15.200.101 # 本机IP地址
   wsrep_node_name=node01 # 本机主机名，唯一
   wsrep_cluster_name=zxh # 集群的名字，所有主机相同
   pxc_strict_mode=ENFORCING
   wsrep_sst_method=xtrabackup-v2
   wsrep_provider_options="socket.ssl=yes;socket.ssl_ca=/etc/mysql/certs/ca.pem;socket.ssl_cert=/etc/mysql/certs/server-cert.pem;socket.ssl_key=/etc/mysql/certs/server-key.pem"
   ssl-ca=/etc/mysql/certs/ca.pem
   ssl-cert=/etc/mysql/certs/server-cert.pem
   ssl-key=/etc/mysql/certs/server-key.pem
   [sst]
   encrypt=4
   ssl-ca=/etc/mysql/certs/ca.pem
   ssl-cert=/etc/mysql/certs/server-cert.pem
   ssl-key=/etc/mysql/certs/server-key.pem
   ```

   分别在三台主机上写入my.cnf文件

7. 启动节点

   ```shell
   # 启动第一个节点
   systemctl start mysql@bootstrap.service
   # 查看随机密码
   grep 'temporary password' /var/log/mysqld.log
   # 修改密码
   mysql -uroot -p'[密码]'
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'rootPass'
   exit
   # 启动第二个节点
   systemctl start mysql
   ## 创建数据库进行测试（可有可无）
   mysql -uroot -p'rootPass' -e "create database 6ecc;"
   # 启动第三个节点
   systemctl start mysql
   # 查询数据库同步情况
   mysql -uroot -p'rootPass' -e "show databases;"
   ```

   ```mysql
   # 数据库进行授权
   CREATE USER 'root'@'10.15.200.%' IDENTIFIED BY 'rootPass';
   GRANT ALL PRIVILEGES ON *.* TO 'root'@'10.15.200.%' WITH GRANT OPTION;
   ```

------

## keepalived+nginx反向代理

1. 安装keepalived

   1. ha01:

      ```shell
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
          }
      }" > /etc/keepalived/keepalived.conf
      ```

   2. ha02:

      ```shell
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
          }
      }" > /etc/keepalived/keepalived.conf
      ```

2. 导入nginx-1.26.0压缩包并解压

   ```shell
   yum -yq install gcc zlib-devel pcre-devel
   tar -xf nginx-1.26.0.tar.gz
   cd nginx-1.26.0/
   ```

3. 进行编译安装nginx

   ```shell
   ./configure --prefix=/usr/local/nginx --conf-path=/etc/nginx/nginx.conf --user=nginx --group=nginx --with-stream --sbin-path=/usr/sbin/nginx
   make ; make install
   useradd nginx
   ```

4. 编辑nginx配置文件

   ```shell
   echo "stream {
       upstream mysql_nodes {
           server 10.15.200.101:3306 weight=1 max_fails=3 fail_timeout=30s;
           server 10.15.200.102:3306 weight=1 max_fails=3 fail_timeout=30s;
           server 10.15.200.103:3306 weight=1 max_fails=3 fail_timeout=30s;
       }
   
       server {
           listen 3306;
           proxy_pass mysql_nodes;
       }
   }" >> /etc/nginx/nginx.conf
   ```

------

## nginx+php

1. 安装nginx与php

   ```shell
   # 源码编译nginx
   yum -yq install gcc zlib-devel pcre-devel
   tar -xf nginx-1.26.0.tar.gz
   cd nginx-1.26.0/
   ./configure --prefix=/usr/local/nginx --conf-path=/etc/nginx/nginx.conf --user=nginx --group=nginx --sbin-path=/usr/sbin/nginx
   make ; make install
   useradd nginx
   # 安装php
   yum -yq install php php-mysqlnd
   # 查看php监听
   cat /etc/php-fpm.d/www.conf |grep 'listen ='
   # 更改nginx配置文件，释放php字段
   location ~ \.php$ {
       root           html;
       fastcgi_pass   unix:/run/php-fpm/www.sock;
       # 改为php监听位置，unix为套接字
       fastcgi_index  index.php;
       fastcgi_param  SCRIPT_FILENAME  /usr/local/nginx/html$fastcgi_script_name;
       include        fastcgi_params;
   }
   # 检查nginx语法
   nginx -t
   # 启动nginx
   nginx
   # 创建php网页文件
   vim /usr/local/nginx/html/index.php
   <?php
     $host='10.15.200.116';
     $username='root';
     $password='rootPass';
     $database='mysql';
     try {
       $mysqli = new mysqli($host, $username, $password, $database);
       $query = "SHOW VARIABLES LIKE 'hostname'";
       $result = $mysqli->query($query);
       if ($result) {
           while ($row = $result->fetch_assoc()) {
             echo "数据库主机名: " . $row["Value"];
           }
       } else {
           echo "查询错误: " . $conn->error;
       };
       $result->free();
     } catch (Exception $e) {
       die('恭喜恭喜, 数据库连接失败~~~');
     }
     $mysqli->close();
   ?>
   ```

2. 浏览器验证

   http://10.15.200.104/index.php

   网页显示：数据库主机名: node01.example.cn