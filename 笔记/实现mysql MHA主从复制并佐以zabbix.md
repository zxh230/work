==启动node01,node02,node03,node05作为mha集群（可自行替换主机）==

mysql节点：node01(主)，node02(从)，node03(从)
zabbix节点：node04(主)，被监控端：node02.03,ha01,02

------

### MHA主从复制

配置主从服务器

1. 全部主机配置

   ```shell
   # 解压后配置yum库
   tar -xf mha.tgz 
   #### 所有节点修改仓库！！！
   echo "[BaaseOS]
   name=BaaseOS
   baseurl=file:///root/mha/
   gpgcheck=0
   enabled=1" >> /etc/yum.repos.d/rocky9.repo
   ####
   # 传到其他主机
   for h in node0{1，2，3，5}
   do
   scp -rq mha/ $h:/root/
   done
   # 传到其他主机
   for h in node0{1，2，3，5}
   do
   scp -rq /etc/yum.repos.d/rocky9.repo $h:/etc/yum.repos.d/rocky9.repo
   done
   # 安装mha
   for h in node0{1，2，3，5}
   do
   ssh -q $h "yum -yq install mha4mysql-node-0.58"
   done
   ```

2. node01主，node02,node03从，node05管理端

   ```shell
   # 这里是主节点
   # 安装mariadb.server
   for h in node0{1，2，3，5}
   do
   ssh -q $h "yum -yq install mariadb-server"
   done
   # 修改配置文件my.cnf，server_id保持唯一，每个节点修改
   [mysqld]
   datadir=/var/lib/mysql
   socket=/var/lib/mysql/mysql.sock
   log_bin                   = /var/lib/mysql/bin-log
   log_bin_index             = /var/lib/mysql/mysql-bin.index
   expire_logs_days          = 7
   server_id                 = 101  # 每个节点唯一，不能相同
   binlog_format             = ROW
   symbolic-links=0
   binlog-ignore-db=performance_schema
   binlog-ignore-db=mysql
   [mysqld_safe]
   log-error=/var/log/mariadb/mariadb.log
   pid-file=/var/run/mariadb/mariadb.pid
   !includedir /etc/my.cnf.d
   # 启动数据库（主）
   systemctl start mariadb-server
   # 更改数据库密码权限
   ALTER USER 'root'@'localhost' IDENTIFIED BY '!@#qweASD69';
   grant replication slave on *.*  to zhaojiedong@'10.15.200.%' identified by '!@#qweASD69';
   grant all on *.* to manager@'10.15.200.%' identified by '!@#qweASD69';
   flush privileges;
   # 查看主节点位置
   show master status\G;
   ```

   从节点配置：

   ```shell
   # 启动数据库
   systemctl start mariadb
   # 更改数据库密码权限
   ALTER USER 'root'@'localhost' IDENTIFIED BY '!@#qweASD69';
   grant replication slave on *.*  to zhaojiedong@'10.15.200.%' identified by '!@#qweASD69';
   grant all on *.* to manager@'10.15.200.%' identified by '!@#qweASD69';
   flush privileges;
   # 连接主节点
   CHANGE MASTER TO
   MASTER_HOST='10.15.200.101',
   MASTER_PORT=3306,
   MASTER_LOG_FILE='bin-log.000002',
   MASTER_LOG_POS=1008,
   MASTER_USER='zhaojiedong',
   MASTER_PASSWORD='96ASDqwer#@!';
   # 启动slave
   start slave;
   ```

3. node05（管理端）

   移动文件并修改

   ```shell
   # 下载mha
   yum install mha4mysql-node-0.58 mha4mysql-manager-0.58 -y
   # 移动文件
   mkdir -p /etc/mha/scripts
   mv master_ip_failover master_ip_online_change send_report /etc/mha/scripts
   # 更改权限
   chmod +x /etc/mha/scripts/*
   ```

   修改app.conf

   将app.conf移动到/etc/mha/

   mv app.conf /etc/mha/

   mv  masterha_default.cnf /etc/

   #### node01:

   mv NodeUtil.pm  /usr/share/perl5/vendor_perl/MHA/NodeUtil.pm

   #### node03添加vip

   ifconfig ens160:66 10.15.200.166/24

   #### node03,node02,node04,node05:

   mv SlaveUtil.pm /usr/share/perl5/vendor_perl/MHA/SlaveUtil.pm

   查看mha状态

   ```shell
   # 检查ssh状态
   masterha_check_ssh --conf=/etc/mha/app.cnf
   # 检查主备状态
   masterha_check_repl --conf=/etc/mha/app.cnf
   ```

   运行mha

   ```shell
   masterha_manager --conf=/etc/mha/app.cnf --remove_dead_master_conf --ignore_last_failover < /dev/null > /var/log/mha/app/manager.log 2>&1
   ```

   查看日志

   ```shell
   tail -f /var/log/mha/app/manager.log
   ```

4. 停止node03（主）mariadb

   ```shell
   systemctl stop mariadb.service
   ```

   日志输出完成后发现vip移动到了node02

    ![image-20240606181502139](https://gitee.com/zhaojiedong/img/raw/master/202406061815176.png)

------

### 配置zabbix监控端

1. 监控端(node04)

   ```shell
   # 解压缩zabbix60.tgz
   tar -xf zabbix60.tgz
   # 修改yum仓库
   echo "[BaaseOS]
   name=BaaseOS
   baseurl=file:///root/zabbix60/
   gpgcheck=0
   enabled=1" >> /etc/yum.repos.d/rocky9.repo
   # 发送目录以及仓库配置到被监控端
   for h in {node02,node03,ha01,ha02}
   do scp -rq /etc/yum.repos.d/rocky9.repo $h:/etc/yum.repos.d/rocky9.repo
   scp -rq zabbix60/ $h:/root/
   done
   # 安装zabbix(监控端)
   yum -yq install zabbix-server-mysql zabbix-web-mysql zabbix-apache-conf zabbix-sql-scripts zabbix-selinux-policy zabbix-agent
   # 被监控端
   yum -yq install zabbix-agent
   # 启动mysql
   systemctl start mysql
   # 查看临时密码
   grep 'temporary password' /var/log/mysqld.log
   # 进入mysql
   mysql -uroot -p""
   ```

   ```mysql
   ALTER USER 'root'@'localhost' IDENTIFIED BY '!@#qweASD69';
   create database zabbix character set utf8mb4 collate utf8mb4_bin;
   create user zabbix@localhost identified by '!@#qweASD69';
   grant all privileges on zabbix.* to zabbix@localhost;
   set global log_bin_trust_function_creators = 1;
   ```

   ```shell
   # 导入数据表，密码为!@#qweASD69
   zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix
   ```

   ```mysql
   set global log_bin_trust_function_creators = 0;
   ```

   ```shell
   # 修改配置文件
   vim /etc/zabbix_server.conf
   ###
   LogFile=/var/log/zabbixsrv/zabbix_server.log
   LogFileSize=0
   DebugLevel=3
   PidFile=/run/zabbixsrv/zabbix_server.pid
   DBHost=localhost
   DBName=zabbix
   DBUser=zabbix
   DBPassword=!@#qweASD69
   DBSocket=/var/lib/mysql/mysql.sock
   Timeout=4
   AlertScriptsPath=/usr/local/sbin
   LogSlowQueries=3000
   TmpDir=/var/lib/zabbixsrv/tmp
   StatsAllowedIP=127.0.0.1
   ###
   vim /etc/zabbix_agentd.conf
   ###
   PidFile=/run/zabbix/zabbix_agentd.pid
   LogFile=/var/log/zabbix/zabbix_agentd.log
   LogFileSize=0
   Server=127.0.0.1, <监控端(zabbix-server)ip>
   ServerActive=127.0.0.1, <监控端(zabbix-server)ip>
   Hostname=node04.example.cn
   Include=/etc/zabbix_agentd.conf.d/*.conf
   ###
   sed -i 's/#ServerName www.example.com:80/ServerName node04.example.cn:80/g' /etc/httpd/conf/httpd.conf
   sed -i 's/;date.timezone =/date.timezone = PRC/g' /etc/php.ini
   # 创建目录
   mkdir -p /etc/zabbix_agentd.conf.d/
   # 启动服务
   systemctl restart zabbix-server zabbix-agent httpd php-fpm
   # 自启动
   systemctl enable zabbix-server zabbix-agent httpd php-fpm
   # 切换字体
   mv DejaVuSans.ttf /usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf
   ```

被监控端（node02,node03,ha01,ha02）（IP地址与主机名自行更换）

```shell
# 修改配置文件
vim /etc/zabbix_agentd.conf
###
PidFile=/run/zabbix/zabbix_agentd.pid
LogFile=/var/log/zabbix/zabbix_agentd.log
LogFileSize=0
Server=127.0.0.1, <监控端(zabbix-server)ip>
ServerActive=127.0.0.1, <被监控端ip> ##
Hostname=<被监控端主机名全名> ## 
Include=/etc/zabbix_agentd.conf.d/*.conf
###
# 创建目录
mkdir -p /etc/zabbix_agentd.conf.d/
# 启动
systemctl start zabbix-agent.service
```

------

### 在mysql上创建监控脚本(两个从节点都做)

```shell
cd /usr/local/bin/
vim number.sh  # 随机数监控项
###
#!/bin/bash
random_number=$((RANDOM % 10 + 1))
echo $random_number
###
vim slave.sh
###
#!/bin/bash

MYSQL_USER="root"
MYSQL_PASSWORD="!@#qweASD69"
IO=`mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e "show slave status\G" | grep  Slave_IO_Running | awk '{print $2}'`
SQL=`mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e "show slave status\G" | grep "Slave_SQL_Running:" | awk '{print $2}'`
if [ "$IO" == "Yes" -a "$SQL" == "Yes" ]; then
    echo 1
else
    echo 0
fi
###
vim yanchi.sh
###
#!/bin/bash

MYSQL_USER="root"
MYSQL_PASSWORD="!@#qweASD69"

relay=$(mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e 'show slave status\G' 2> /dev/null | grep Seconds_Behind_Master | awk '{print $2}')
echo $relay
###
# 现在应该有3个脚本文件，授权
chmod 777 *
# 修改zabbix-agent监控文件
echo "UserParameter=slave,/usr/local/bin/slave.sh" > /etc/zabbix_agentd.conf.d/mysql_slave_status.conf
echo "UserParameter=number,/usr/local/bin/number.sh" > /etc/zabbix_agentd.conf.d/mysql_random_number.conf
echo "UserParameter=yanchi,/usr/local/bin/yanchi.sh" > /etc/zabbix_agentd.conf.d/mysql_replication_delay.conf
# 重启agent
systemctl restart zabbix-agent
# 在监控端验证
zabbix_get  -s <mysql从节点ip> -p 10050 -k "yanchi"
zabbix_get  -s <mysql从节点ip> -p 10050 -k "number"
zabbix_get  -s <mysql从节点ip> -p 10050 -k "slave"
# 监控nginx_active（安装nginx节点自定）
yum -yq install nginx
vim /etc/nginx/conf.d/aaa.conf
###
server {
    listen  *:2407 default_server;
    server_name node05.example.cn;
    location /nginx_status   {
        stub_status on;
        access_log off;
        #allow 127.0.0.1;
        #deny all;
    }
}
###
systemctl start nginx
# 编写脚本
vim /active.sh
###
/usr/bin/curl "http://127.0.0.1:2407/nginx_status" 2>/dev/null| grep 'Active' | awk '{print $NF}'
###
# 创建配置文件
vim /etc/zabbix_agentd.conf.d/active.conf
###
UserParameter=nginx_active[*],/usr/local/bin/active.sh
###
# 使其生效
chmod 777 /usr/local/bin/active.sh
systemctl restart zabbix-agent
# 在zabbix上进行查询
zabbix_get  -s <nginx节点ip> -p 10050 -k "nginx_active"
```

------

### 监控haproxy

```shell
# 首先应在两台haproxy上安装zabbix-agent并且配置完成
```

```shell
# 配置keepalived(两台，第二台自行修改##标注位置)
yum -yq install keepalived
# 配置
vim /etc/keepalived/keepalived.conf 
###
global_defs {
    router_id <hostname> ##
}
vrrp_instance node_http {
    state BACKUP
    interface ens160
    virtual_router_id 116
    priority 120  ##
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass ha0102
    }
    virtual_ipaddress {
        10.15.200.116
    }
}
###
# 启动
systemctl start keepalived.service 
```

```shell
# 安装haproxy（两台，配置相同，完全一样）
yum -yq install haproxy
# 配置
vim /etc/haproxy/haproxy.cfg 
###
global
    log 127.0.0.1   local0
    log 127.0.0.1   local1 notice
    #log loghost    local0 info
    maxconn 4096
    chroot /usr/share/haproxy
    uid 99
    gid 99
    #debug
    #quiet

defaults
    log     global
    mode    tcp
    option  tcplog
    option  dontlognull
    retries 3
#   redispatch
    maxconn 2000
    timeout connect 5000
    timeout client  50000
    timeout server  50000

listen mysql-cluster
    bind 0.0.0.0:3306
    mode tcp
    balance roundrobin
    option mysql-check user haproxy_check
    server db1 10.15.200.102:3306 check inter 2000 fall 3
    server db2 10.15.200.103:3306 check inter 2000 fall 3
###自行添加/修改后端节点，复制后修改ip即可
# 启动
systemctl start haproxy
# 安装软件包
yum -yq install nmap-ncat-3:7.91-10.el9.x86_64
# 编写监控脚本
vim /usr/local/bin/kan.sh 
###
#!/bin/bash
BACKEND_NODES="10.15.200.102 10.15.200.103"
check_node_port() {
    local node=$1
    ncat -z -w 2 $node 3306 > /dev/null 2>&1
    return $?
}
main() {
    local alive_count=0

    for node in $BACKEND_NODES; do
        if check_node_port $node; then
            alive_count=$((alive_count + 1))
        fi
    done

    echo $alive_count
}
main
###
# 运行脚本验证,输出数字等于haproxy设定的后端节点数即可
sh kan.sh
# 配置
echo "UserParameter=kan,/usr/local/bin/yanchi.sh" > /etc/zabbix_agentd.conf.d/kan.conf
# 主节点验证
zabbix_get  -s <haproxy节点ip> -p 10050 -k "kan"
```

