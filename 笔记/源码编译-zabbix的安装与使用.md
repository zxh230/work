系统环境：
	node01.example.cn	10.15.200.101
	node02.example.cn	10.15.200.102
均已关闭防火墙与 selinux，并且配置 dns 解析
![image.png](https://raw.githubusercontent.com/zxh230/image-/main/图片/20250320143510.png)

------
开始安装

```shell
# 在官网下载zabbix源码包
wget https://cdn.zabbix.com/zabbix/sources/stable/7.2/zabbix-7.2.4.tar.gz
# zabbix官网：https://www.zabbix.com/download_sources
# 解压并准备安装
tar -zxvf zabbix-7.2.4.tar.gz 
groupadd --system zabbix
useradd --system -g zabbix -d /usr/lib/zabbix -s /sbin/nologin -c "Zabbix Monitoring System" zabbix
yum -y install mariadb-server
systemctl start mariadb
mysql
```

配置数据库

```mysql
create database zabbix character set utf8mb4 collate utf8mb4_bin;
create user 'zabbix'@'localhost' identified by '123.com';
grant all privileges on zabbix.* to 'zabbix'@'localhost';
SET GLOBAL log_bin_trust_function_creators = 1;
quit
```

导入数据库

```shell
cd /root/zabbix-7.2.4/database/mysql
mysql -uzabbix -p123.com zabbix < schema.sql
mysql -uzabbix -p123.com zabbix < images.sql
mysql -uzabbix -p123.com zabbix < data.sql
# 进入mysql禁用log_bin_trust_function_creators
mysql -uroot -p123.com
SET GLOBAL log_bin_trust_function_creators = 0;
quit
# 编译

```