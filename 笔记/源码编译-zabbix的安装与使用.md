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

```