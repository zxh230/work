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
# 
```