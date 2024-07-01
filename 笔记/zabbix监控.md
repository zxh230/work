### zabbix: 监控nginx  active / redis qps / mysql select

### jenkins: 发布java项目到 tomcat

------

#### zabbix

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
   for h in node0{5,6,7}
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
   Server=127.0.0.1, 10.15.200.104
   ServerActive=127.0.0.1, 10.15.200.104
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

2. 被监控端（node05,node06,node07）

   ```shell
   # 修改配置文件
   vim /etc/zabbix_agentd.conf
   ###
   PidFile=/run/zabbix/zabbix_agentd.pid
   LogFile=/var/log/zabbix/zabbix_agentd.log
   LogFileSize=0
   Server=127.0.0.1, 10.15.200.104
   ServerActive=127.0.0.1, 10.15.200.105 ##
   Hostname=node05.example.cn ## 
   Include=/etc/zabbix_agentd.conf.d/*.conf
   ###
   # 创建目录
   mkdir -p /etc/zabbix_agentd.conf.d/
   # 启动
   systemctl start zabbix-agent.service
   ```

   进入zabbix网页端

   http://node04.example.cn/zabbix

3. web端配置

   创建主机组node

   ![image-20240619113115529](https://gitee.com/zhaojiedong/img/raw/master/202406191131658.png)

   ![image-20240619113135704](https://gitee.com/zhaojiedong/img/raw/master/202406191131743.png)

   添加监控主机

   ![image-20240619113337618](https://gitee.com/zhaojiedong/img/raw/master/202406191133678.png)

   依次添加node06,node07

   编写脚本并创建模板

   ```shell
   # node05(nginx)
   yum -yq install nginx
   vim /etc/nginx/conf.d/aaa.conf
   ###
   server {
       listen  *:80 default_server;
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
   /usr/bin/curl "http://127.0.0.1:80/nginx_status" 2>/dev/null| grep 'Active' | awk '{print $NF}'
   ###
   # 创建配置文件
   vim /etc/zabbix_agentd.conf.d/active.conf
   ###
   UserParameter=nginx_active[*],/active.sh
   ###
   # 使其生效
   chmod 777 /active.sh
   systemctl restart zabbix-agent
   # 在zabbix上进行查询
   zabbix_get  -s 10.15.200.105 -p 10050 -k "nginx_active"
   ```

   ```shell
   # node06(redis)
   yum -yq install redis
   # 修改配置文件
   vim +75 /etc/redis/redis.conf # 将127.0.0.1修改为0.0.0.0，其他不变
   systemctl start redis
   # 写入脚本
   vim /redis.sh
   ###
   redis-cli info | grep ops |awk -F: '{print $2}'
   ###
   vim /etc/zabbix_agentd.conf.d/redis.conf
   ###
   UserParameter=redis_qps[*],/redis.sh
   ###
   systemctl restart zabbix-agent
   # 使其生效
   chmod 777 /redis.sh
   # 前往zabbix进行查询
   zabbix_get  -s 10.15.200.106 -p 10050 -k "redis_qps"
   ```

   ```shell
   # node07(mysql)
   # 导入压缩包
   tar -xf Percona-XtraDB-Cluster.el9.tgz
   echo "[AappStream]
   name=AappStream
   baseurl=file:///root/Percona-XtraDB-Cluster/
   gpgcheck=0
   enabled=1" >> /etc/yum.repos.d/rocky9.repo
   yum -yq install mariadb-server
   grep 'temporary password' /var/log/mysqld.log
   mysql -uroot -p''
   ALTER USER 'root'@'localhost' IDENTIFIED BY '!@#qweASD69';
   exit;
   # 创建脚本
   yum -yq install python3
   vim /aaa.py
   ```

   ```python
   #!/usr/bin/env python3
   import subprocess
   import time
   import os
   
   # MySQL连接信息
   MYSQL_USER = "root"
   MYSQL_PASSWORD = "!@#qweASD69"
   MYSQL_COMMAND = "SHOW GLOBAL STATUS LIKE 'Questions';"
   
   # 时间间隔（秒）
   TIME = 1
   
   # MySQL查询命令
   mysql_command = f"mysql -u{MYSQL_USER} -p'{MYSQL_PASSWORD}' -e \"{MYSQL_COMMAND}\""
   
   try:
       # 获取旧的查询次数
       old_query_output = subprocess.run(mysql_command, shell=True, capture_output=True, text=True, check=True)
       old_query = int(old_query_output.stdout.split('\n')[1].split()[1])
   
       # 等待指定时间
       time.sleep(TIME)
   
       # 获取新的查询次数
       new_query_output = subprocess.run(mysql_command, shell=True, capture_output=True, text=True, check=True)
       new_query = int(new_query_output.stdout.split('\n')[1].split()[1])
   
       # 计算查询次数差值
       time_query = new_query - old_query
   
       # 计算QPS
       if TIME > 0:
           qps = time_query / TIME
           print(f"{qps}")
       else:
           print("0.0")
   
   except subprocess.CalledProcessError as e:
       print(f"Error executing MySQL command: {e}")
   except IndexError:
       print("Error: Unexpected output format from MySQL command.")
   except ValueError:
       print("Error: Failed to convert query counts to integers.")
   except Exception as e:
       print(f"Unexpected error: {e}")
   ```

   ```shell
   # 创建配置文件
   vim /etc/zabbix_agentd.conf.d/mysql.conf
   ###
   UserParameter=mysql_qps[*],/aaa.py
   ###
   systemctl restart zabbix-agent
   # 使其生效
   chmod 777 /aaa.py
   # 前往zabbix进行查询
   zabbix_get -s 10.15.200.107 -p 10050 -k "mysql_qps"
   ```

4. 回到web网页

   创建模板

   ![image-20240619113505883](https://gitee.com/zhaojiedong/img/raw/master/202406191135914.png)

   依次创建模板redis和mysql

   ![image-20240619113427596](https://gitee.com/zhaojiedong/img/raw/master/202406191134637.png)

   配置item项目

   nginx：

   进入nginx模板，新建items ==(Key为zabbix监控端验证时查询的条目)==

   ![image-20240618172909050](https://gitee.com/zhaojiedong/img/raw/master/202406181729081.png)

   redis：

   进入模板，新建项目

   ![image-20240618173534365](https://gitee.com/zhaojiedong/img/raw/master/202406181735411.png)

   mysql：

   进入模板，新建项目

   ![image-20240618173801646](https://gitee.com/zhaojiedong/img/raw/master/202406181738700.png)

   配置nginx模板触发器

   Create trigger：

   Name：{HOST.NAME}_nginx活跃数异常

   Expression：avg(/nginx/nginx_active,#3)>20

   配置redis模板触发器

   Create trigger：

   Name：{HOST.NAME}_redis操作数异常

   Expression：max(/redis/redis_qps,3)>20000

   配置mysql触发器

   Create trigger：

   Name：{HOST.NAME}_mysql操作数异常

   Expression：max(/mysql/mysql_qps,1)>1000

   依次为三个模板生成图表

   ![image-20240618173948150](https://gitee.com/zhaojiedong/img/raw/master/202406181739198.png)

   ![image-20240618174104380](https://gitee.com/zhaojiedong/img/raw/master/202406181741439.png)

   创建完成后主机绑定模板

   ![image-20240619114526224](https://gitee.com/zhaojiedong/img/raw/master/202406191145270.png)

   查看图表

   ![image-20240618174307655](https://gitee.com/zhaojiedong/img/raw/master/202406181743698.png)

   ![image-20240618174233306](https://gitee.com/zhaojiedong/img/raw/master/202406181742359.png)

   ![image-20240618174353433](https://gitee.com/zhaojiedong/img/raw/master/202406181743485.png)

5. 配置邮件报警

   ```shell
   # zabbix
   yum -yq install perl
   # 导入sendEmail文件
   mv sendEmail /usr/local/sbin/
   vim /usr/local/sbin/send-message-by-email.sh 
   ###
   #!/bin/bash
   # 如果是 163.com 的邮箱 -s smtp.163.com
   # 如果是 qq.com  的邮箱 -s smtp.qq.com
   to=$1
   subject=$2
   body=$3
   /usr/local/sbin/sendEmail  -f 2302120216@qq.com -t "$to" -s smtp.qq.com \
   -xu 2302120216@qq.com -xp 'izjwqjwzyrmbdigd' \
   -o tls=no -o message-charset=utf8 -u "$subject" -m "$body" \
   -l /tmp/send-message-by-email.log
   ###
   # 验证
   send-message-by-email.sh 自己的邮箱地址 "Subject" "Body of the email"
   ```

   创建媒介

   ![image-20240618175140594](https://gitee.com/zhaojiedong/img/raw/master/202406181751651.png)

   ![image-20240618180328641](https://gitee.com/zhaojiedong/img/raw/master/202406181803691.png)

   ![image-20240618180509697](https://gitee.com/zhaojiedong/img/raw/master/202406181805736.png)

   ![image-20240618180433345](https://gitee.com/zhaojiedong/img/raw/master/202406181804390.png)

   ![image-20240618180632899](https://gitee.com/zhaojiedong/img/raw/master/202406181806946.png)

   ```shell
   #
   故障_{TRIGGER.STATUS}:{TRIGGER.NAME}故障_{TRIGGER.STATUS}:{TRIGGER.NAME}
   #
   已经恢复_{TRIGGER.STATUS}:{TRIGGER.NAME}
   #
   服务器主机:{HOST.NAME}
   服务器地址:{HOST.IP}
   服务器时间:{EVENT.DATE} {EVENT.TIME}
   服务器信息:{TRIGGER.NAME}
   触发器状态:{TRIGGER.STATUS}
   触发器级别:{TRIGGER.SEVERITY}
   监控信息如下:
   1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}
   ```

   创建用户

   ![image-20240618181235529](https://gitee.com/zhaojiedong/img/raw/master/202406181812585.png)

   ![image-20240618181322465](https://gitee.com/zhaojiedong/img/raw/master/202406181813499.png)

   ### 注：密码有复杂性要求

   ![image-20240618181456053](https://gitee.com/zhaojiedong/img/raw/master/202406181814092.png)

   ![image-20240618181521485](https://gitee.com/zhaojiedong/img/raw/master/202406181815529.png)

   创建动作

   ![image-20240618180745576](https://gitee.com/zhaojiedong/img/raw/master/202406181807603.png)

![image-20240618180815382](https://gitee.com/zhaojiedong/img/raw/master/202406181808436.png)

![image-20240618180848005](https://gitee.com/zhaojiedong/img/raw/master/202406181808033.png)

![image-20240618180909972](https://gitee.com/zhaojiedong/img/raw/master/202406181809008.png)

![image-20240618180940538](https://gitee.com/zhaojiedong/img/raw/master/202406181809595.png)

![image-20240618181029936](https://gitee.com/zhaojiedong/img/raw/master/202406181810971.png)

进行压力测试

```shell
# nginx
yum -yq install httpd-tools-2.4.53-7.el9.x86_64
ab -c 100 -n 1000000 http://10.15.200.105/nginx_status
# redis
redis-benchmark -h 10.15.200.106 -p 6379 -n 100000 -c 20
# mysql 未能实现
mysqlslap -uroot -p'!@#qweASD69' --auto-generate-sql -concurrency=9999999
```

------

测试mysql报警

将mysql模板中触发器下调为1000

![image-20240619121001747](https://gitee.com/zhaojiedong/img/raw/master/202406191210809.png)

------

### 配置jenkins发布java到tomcat

git.example.cn: 提供git仓库

node08: 配置jenkins

node09: 配置tomcat

##### node8:

```shell
# 安装软件包
yum install -yq java-11-openjdk maven-openjdk11 git
# 从jenkins上导入包
scp jenkins:/root/jenkins_2.426.2.plugins.tgz .
scp jenkins:/root/jenkins_2.426.2.war .
# 配置
tar -xf jenkins_2.426.2.plugins.tgz
# 克隆远端仓库
cd /tmp/
ls
rm -rf *
git clone git@git.example.cn:/home/git/repos/helloworld.git
cd helloworld/
mvn clean install -D maven.test.skip=true
```

##### node09:

```shell
# 安装tomcat
yum -yq install java-11-openjdk
tar -xf apache-tomcat-10.1.13.tar.gz
mv apache-tomcat-10.1.13 /usr/local/tomcat
cd /usr/local/tomcat/
# 修改配置文件
vim /usr/local/tomcat/conf/tomcat-users.xml +21
### 添加
<role rolename="admin-gui"/>
<role rolename="manager-gui"/>
<role rolename="manager-script"/>
<user username="admin" password="admin" roles="admin-gui,manager-gui,manager-script"/>
###
sed -i 's/127/10/g' /usr/local/tomcat/webapps/{docs,examples,host-manager,manager}/META-INF/context.xml
```

![image-20240620092751309](https://gitee.com/zhaojiedong/img/raw/master/202406200927405.png)

```shell
# 启动tomcat
/usr/local/tomcat/bin/startup.sh
```

#### 配置jenkins任务

新建任务

任务名为：mvn-helloworld

风格为：构建一个maven项目

1. 任务配置

   描述：java mvn to tomcat

   源码管理选择git

   ##### 新建Credentials：

   类型选择ssh密钥对

   ![image-20240620093231668](https://gitee.com/zhaojiedong/img/raw/master/202406200932721.png)

   id为git

   username：git

   新建密钥

   ![image-20240620093327346](https://gitee.com/zhaojiedong/img/raw/master/202406200933397.png)

   ==密钥：==

   ```shell
   # git.example.cn
   su - git
   cat .ssh/id_rsa
   ### 全复制！
   ```

   添加后：![image-20240620093549622](https://gitee.com/zhaojiedong/img/raw/master/202406200935665.png)

   配置git仓库URL

   ![image-20240617095619938](https://gitee.com/zhaojiedong/img/raw/master/202406170956964.png)

   Build配置：

   Goals and options：

   clean install -D maven.test.skip=true

![image-20240617095805005](https://gitee.com/zhaojiedong/img/raw/master/202406170958029.png)

构建后操作选择**Deploy war/ear to a container**

==添加Credentials：==

用户名：admin

密码：	admin

id：		tomcat

![image-20240617100309590](https://gitee.com/zhaojiedong/img/raw/master/202406171003625.png)

###### 保存任务后运行

在node08上验证：

```shell
curl 10.15.200.109:8080/hello/
```

![image-20240620093823198](https://gitee.com/zhaojiedong/img/raw/master/202406200938251.png)
