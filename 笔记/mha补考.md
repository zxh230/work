补考：要求

```txt
	按如下要求搭建MHA集群:
	vip: 10.15.200.166   虚拟网卡名字: ensxxx:66
	root密码: 96ASDqwer#@!
	主从复制帐号: yourname (比如: zhangjianxin)  密码: 96ASDqwer#@!
	监控端帐号: manager 密码: 96ASDqwer#@!
	node01 监控端:				node02 为候选节点
	node04 为从节点
	node05 为从节点
	node03 为主节点
	模拟node03故障, 达到预期的故障转移, node03 再重新加入集群, 形成新的MHA集群
```

------

配置主从服务器

1. 全部主机配置

   ```shell
   # 解压后配置yum库
   tar -xf mha.tgz 
   echo "[BaaseOS]
   name=BaaseOS
   baseurl=file:///root/mha/
   gpgcheck=0
   enabled=1" >> /etc/yum.repos.d/rocky9.repo
   # 传到其他主机
   for h in node0{1..5}
   do
   scp -rq mha/ $h:/root/
   done
   # 传到其他主机
   for h in node0{1..5}
   do
   scp -rq /etc/yum.repos.d/rocky9.repo $h:/etc/yum.repos.d/rocky9.repo
   done
   # 安装mha
   for h in node0{1..5}
   do
   ssh -q $h "yum -yq install mha4mysql-node-0.58"
   done
   ```

2. node03（主），node02（从），node04（从），node05（从）：

   ```shell
   # 安装mariadb.server
   for h in node0{2..5}
   do
   ssh -q $h "yum -yq install mariadb-server"
   done
   # 修改配置文件my.cnf，server_id保持唯一
   [mysqld]
   datadir=/var/lib/mysql
   socket=/var/lib/mysql/mysql.sock
   log_bin                   = /var/lib/mysql/bin-log
   log_bin_index             = /var/lib/mysql/mysql-bin.index
   expire_logs_days          = 7
   server_id                 = 101
   binlog_format             = ROW
   symbolic-links=0
   binlog-ignore-db=performance_schema
   binlog-ignore-db=mysql
   [mysqld_safe]
   log-error=/var/log/mariadb/mariadb.log
   pid-file=/var/run/mariadb/mariadb.pid
   !includedir /etc/my.cnf.d
   # 启动数据库
   systemctl start mariadb
   # 更改数据库密码权限
   ALTER USER 'root'@'localhost' IDENTIFIED BY '96ASDqwer#@!';
   grant replication slave on *.*  to zhaojiedong@'10.15.200.%' identified by '96ASDqwer#@!';
   grant all on *.* to manager@'10.15.200.%' identified by '96ASDqwer#@!';
   flush privileges;
   # 查看主节点位置
   show master status\G;
   ```

   从节点配置：

   ```shell
   # 启动数据库
   systemctl start mariadb
   # 更改数据库密码权限
   ALTER USER 'root'@'localhost' IDENTIFIED BY '96ASDqwer#@!';
   grant replication slave on *.*  to zhaojiedong@'10.15.200.%' identified by '96ASDqwer#@!';
   grant all on *.* to manager@'10.15.200.%' identified by '96ASDqwer#@!';
   flush privileges;
   # 连接主节点
   CHANGE MASTER TO
   MASTER_HOST='10.15.200.103',
   MASTER_PORT=3306,
   MASTER_LOG_FILE='bin-log.000002',
   MASTER_LOG_POS=1011,
   MASTER_USER='zhaojiedong',
   MASTER_PASSWORD='96ASDqwer#@!';
   # 启动slave
   start slave;
   ```

3. node01（管理端）

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

   修改

   vim master_ip_failover

   ![image-20240606174248517](https://gitee.com/zhaojiedong/img/raw/master/202406061742595.png)

   vim master_ip_online_change

   ![image-20240606174337237](https://gitee.com/zhaojiedong/img/raw/master/202406061743264.png)

   将app.conf移动到/etc/mha/

   mv app.conf /etc/mha/

   vim /etc/mha/app.conf

   ```shell
   [server default]
   manager_log=/var/log/mha/app/manager.log
   manager_workdir=/var/log/mha/app
   
   [server1]
   candidate_master=1
   hostname=node03
   master_binlog_dir="/var/lib/mysql"
   
   [server2]
   candidate_master=1
   hostname=node02
   master_binlog_dir="/var/lib/mysql"
   
   [server3]
   candidate_master=1
   hostname=node04
   master_binlog_dir="/var/lib/mysql"
   
   [server4]
   hostname=node05
   master_binlog_dir="/var/lib/mysql"
   no_master=1
   ```

   ![image-20240606180747695](https://gitee.com/zhaojiedong/img/raw/master/202406061807729.png)

   将脚本文件移动到指定位置

   mv  masterha_default.cnf /etc/

   vim /etc/masterha_default.cnf

   ```shell
   [server default]
   user=manager
   password='96ASDqwer#@!'
   ssh_user=root
   repl_user=zhaojiedong
   repl_password='96ASDqwer#@!'
   ping_interval=1
   secondary_check_script=/usr/bin/masterha_secondary_check -s node03 -s node02 -s node04 -s node05
   master_ip_failover_script="/etc/mha/scripts/master_ip_failover"
   master_ip_online_change_script="/etc/mha/scripts/master_ip_online_change"
   report_script="/etc/mha/scripts/send_report"
   ```

   ![image-20240606180932500](https://gitee.com/zhaojiedong/img/raw/master/202406061809536.png)

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