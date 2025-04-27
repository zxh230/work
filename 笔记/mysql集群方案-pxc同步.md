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
[mysqld]
# 每个节点的唯一标识*
server-id=1
# 二进制日志格式
binlog_format=ROW
# 默认存储引擎
default_storage_engine=InnoDB
# InnoDB 自增锁模式
innodb_autoinc_lock_mode=2
[galera]
# Galera 插件路径
wsrep_provider=/usr/lib64/galera3/libgalera_smm.so
# 集群名称
wsrep_cluster_name=pxc-cluster
# 集群节点地址列表*
wsrep_cluster_address=gcomm://10.15.200.101,10.15.200.102,10.15.200.103
# 当前节点名称*
wsrep_node_name=node01
# 当前节点地址*
wsrep_node_address=10.15.200.101
# 同步方法及认证信息
wsrep_sst_method=xtrabackup-v2
wsrep_sst_auth=sstuser:123456
# PXC 严格模式
pxc_strict_mode=ENFORCING
[client]
socket=/var/lib/mysql/mysql.sock
###
(将三台系统上的配置文件依次更改)
# 启动mysql  (node01)
systemctl start mysql@bootstrap.service
# 配置mysql用户，设置密码
CREATE USER 'sstuser'@'localhost' IDENTIFIED BY '123456';
GRANT RELOAD, LOCK TABLES, PROCESS, REPLICATION CLIENT ON *.* TO 'sstuser'@'localhost';
FLUSH PRIVILEGES;
# node02,node03正常启动mysql
systemctl start mysql
```

启动后，进入 mysql 查看
```mysql
# 将[root_password]更改为自己的root-mysql密码
mysql -uroot -p"[root_password]"
show status like 'wsrep%';
# 检查输出信息中wsrep_cluster_size的数值是否为3，该信息为集群节点数量
```