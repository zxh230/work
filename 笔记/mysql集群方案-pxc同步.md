系统环境：
系统为 pxc 批量装机的系统，网段为 10.15.200.0/24
网关：10.15.200.254
node 01：10.15.200.101
node 02：10.15.200.102
node 03：10.15.200.103
均已关闭防火墙与 selinux

#### 1. 安装 Percona-XtraDB-Cluster-57

node 01~node 03
```shell
# 安装yum库
for h in {1..3}; do ssh node0$h "yum install https://repo.percona.com/yum/percona-release-latest.noarch.rpm";done
# 启用
for h in {1..3}; do ssh node0$h "percona-release setup pxc-57";done
# 安装
for h in {1..3}; do ssh node0$h "yum -y install Percona-XtraDB-Cluster-57";done
# 启动mysql
systemctl start mysql
# 查看随机密码
grep 'temporary password' /var/log/mysqld.log
```
![image.png](https://raw.githubusercontent.com/zxh230/image-/main/图片/20250427174819.png)

```shell
# 更改mysql密码
mysql -uroot -p"oxF+79Mq:Lqr"
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
# 退出并关闭mysql
exit
systemctl stop mysql
# 以上操作在三台系统上操作完全同步与一致
# 更改mysql配置文件(需要更改的位置已使用*标记)(node01~node03)
vim /etc/my.cnf
###
# PXC集群中每个MySQL实例的唯一标识，不能重复*
server-id=1
wsrep_provider=/usr/lib64/galera3/libgalera_smm.so
# PXC集群的名称和所有服务地址*
wsrep_cluster_name=pxc-cluster
wsrep_cluster_address=gcomm://10.15.200.101,10.15.200.102,10.15.200.103
# 当前节点的名称和服务地址*
wsrep_node_name=node01
wsrep_node_address=10.15.200.101
# 指定同步方法和账户信息，这个用户在下文会进行创建
wsrep_sst_method=xtrabackup-v2 
wsrep_sst_auth= sstuser:123456
#开启严厉模式,它会阻止用户执行 Percona XtraDB Cluster 所不支持的功能。
pxc_strict_mode=ENFORCING  
# 指定二进制日志的格式
binlog_format=ROW 
# 指定默认的存储引擎
default_storage_engine=InnoDB 
# Galera 仅支持 InnoDB 的 interleaved(2) 锁定模式:
# 该模式下所有 INSERT SQL 都不会有表级 AUTO-INC 锁,多个语句可以同时执行
innodb_autoinc_lock_mode=2 
###

```