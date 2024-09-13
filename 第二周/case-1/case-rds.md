创建阿里云 RDS 账号

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903184206.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903184227.png)

授权数据库

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903184528.png)

在 Windows 上创建空 txt 文件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903185349.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903185541.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903185604.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903185625.png)

导入成功

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903185721.png)

数据库备份

```shell
# 安装mysql-server
yum -y install mysql-server
systemctl start mysql-server
mysql
##
create database hansir;
use hansir;
create table test1(id int(10) primary key, name varchar(30), age int(10));
exit
# 导出数据库
mysqldump hansir > hansir.sql
# 登录阿里云rds
mysql -uroot -p123_comZXH -h rm-2ze5334ki386dfa25.mysql.rds.aliyuncs.com
create database hansir;
exit
# 导入
mysql -uroot -p123_comZXH -h rm-2ze5334ki386dfa25.mysql.rds.aliyuncs.com hansir < hansir.sql 
# 查看
mysql -uroot -p123_comZXH -h rm-2ze5334ki386dfa25.mysql.rds.aliyuncs.com
show databases;
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904215139.png)
