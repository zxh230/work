修改主机名

启动 gw 主机

```shell
vim  /etc/dhcp/dhcpd.conf
# 修改主机名
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091730962.png)

修改 dns 服务配置

/var/named/example. cn. zone 

修改对应 ip 的主机名

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091732490.png)

/var/named/200.15.10. in-addr. arpa

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091732176.png)

重启 dhcpd 与 named

`systemctl restart named.service dhcpd.service `

开启虚拟机：

zabbixserver（原 node 01）

host 1 (原 node 02)

host 2（原 node 03）

nfs（原 node 04）

验证主机名是否被修改

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736369.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736891.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736927.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736860.png)

******

开始实验：

zabbix
```shell
# 编写部署lnmp
vim lnmp.yml
###
- name: install in lnmp
hosts: host1 host2
tasks:
  - name: get nginx ter
    command: "wget https://nginx.org/download/nginx-1.24.0.tar.gz"
  - name: unarchive
    unarchive:
      src: /root/nginx-1.24.0.tar.gz
      dest: /root/
      remote_src: yes
  - name: install any page
    yum:
      name:
        - gcc
        - openssl
        - pcre-devel
        - zlib-devel
      state: present
  - name: pkg nginx
    shell: "cd /root/nginx-1.24.0/ && ./configure --prefix=/usr/local/nginx --conf-path=/etc/nginx/nginx.conf --sbin-path=/usr/sbin && make -j4 && make install"
    tags:
      - nginx-pass
  - name: install mariadb
    yum:
      name: mariadb-server
      state: present
  - name: install php and plugins
    yum:
      name:
        - php
        - php-mysqli
        - php-mysqlnd
      state: present
  - name: copy nginx.conf
    copy:
      src: nginx.conf
      dest: /etc/nginx/nginx.conf
  - name: copy php conf
    copy: 
      src: www.conf
      dest: /etc/php-fpm.d/www.conf
  - name: copy mysql conf
    copy:
      src: my.cnf
      dest: /etc/my.cnf
  - name: start many service
    service:
      name: "{{ item }}"
      state: started
      enabled: yes
    loop:
      - php-fpm
      - mariadb.service
  - name: start nginx
    command: "nginx"
    tags:
      - start-nginx
  - name: grant
    shell: |
      mysql -e "create user 'root'@'%.%.%.%' identified by '123.com';";
      mysql -e "grant all on *.* to 'root'@'%.%.%.%';"
###
vim zabbix.yml
###
- name: deploy zabbix-server
  hosts: zabbixserver
  tasks:
    - name: unarchive zabbix tar
      unarchive:
        src: zabbix60.tgz
        dest: /root/
    - name: revise yum repo
      copy:
        src: rocky9.repo
        dest: /etc/yum.repos.d/
    - name: install zabbix-server
      yum: 
        name: 
          - zabbix-server-mysql
          - zabbix-web-mysql
          - zabbix-apache-conf
          - zabbix-sql-scripts
          - zabbix-selinux-policy
          - zabbix-agent
        state: present
    - name: start mysql
      service:
        name: mysql
        state: started
        enabled: yes
    - name: 提取 MySQL 临时密码
      shell: "grep 'temporary password' /var/log/mysqld.log | awk -F': ' '{print $2}'"
      register: temp_password_output
    - name: 设置旧密码变量
      set_fact:
        old_passwd: "{{ temp_password_output.stdout }}"
    - name: 更改 root 用户密码
      shell: >
        mysql --connect-expired-password -uroot -p'{{ old_passwd }}'
        -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '!@#qweASD69';"
      tags:
        - mysql-pass
    - name: zabbix create databases
      shell: |
        mysql -uroot -p'!@#qweASD69' -e "
          ALTER USER 'root'@'localhost' IDENTIFIED BY '!@#qweASD69';
          CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
          CREATE USER 'zabbix'@'localhost' IDENTIFIED BY '!@#qweASD69';
          GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix'@'localhost';
          SET GLOBAL log_bin_trust_function_creators = 1;"
      tags:
        - mysql-skip
    - name: 设置全局变量 log_bin_trust_function_creators
      shell: "mysql -uroot -p'!@#qweASD69' -e 'set global log_bin_trust_function_creators = 1;'"
      tags:
        - mysql-skip
    - name: create tables
      shell: "zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p'!@#qweASD69' zabbix"
      tags:
        - mysql-skip
    - name: set global
      shell: "mysql -uroot -p'!@#qweASD69' -e 'set global log_bin_trust_function_creators = 0;'"

    - name: copy server conf
      template:
        src: zabbix_server.j2
        dest: /etc/zabbix_server.conf
    - name: agent conf
      template:
        src: zabbix_agent.j2
        dest: /etc/zabbix_agentd.conf
    - name: sed
      shell: |
           sed -i 's/#ServerName www.example.com:80/ServerName node04.example.cn:80/g' /etc/httpd/conf/httpd.conf;
           sed -i 's/;date.timezone =/date.timezone = PRC/g' /etc/php.ini
    - name: create directory
      file:
        path: /etc/zabbix_agentd.conf.d/
        state: directory
    - name: start zabbix
      service:
        name: "{{ item }}"
        state: started
        enabled: yes
      loop:
        - zabbix-server-mysql.service
        - zabbix-agent
        - httpd
        - php-fpm
    - name: zone
      copy:
        src: DejaVuSans.ttf
        dest: /usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf
- name: zabbix-agent install
  hosts: host1 host2
  tasks:
    - name: unarchive zabbix tar
      unarchive:
        src: zabbix60.tgz
        dest: /root/
    - name: revise yum repo
      copy:
        src: rocky9.repo
        dest: /etc/yum.repos.d/
    - name: install zabbix-server
      yum:
        name: zabbix-agent
        state: present
    - name: copy agent conf
      template:
        src: zabbix_agent.j2
        dest: /etc/zabbix_agentd.conf
    - name: create directory
      file:
        path: /etc/zabbix_agentd.conf.d/
        state: directory
    - name: start agent
      service:
        name: zabbix-agent.service
        state: started
        enabled: yes
###
vim nfs.yml
###
- name: install nfs-server
  hosts: nfs
  tasks:
    - name: install nfs
      yum: 
        name: nfs-utils
        state: present
    - name: copy nfs conf
      template:
        src: exports.j2
        dest: /etc/exports
    - name: create directory 1
      file:
        path: /nfs/lnmp1
        state: directory
        mode: 0775
    - name: create directory 2
      file:
        path: /nfs/lnmp2
        state: directory
        mode: 0775
    - name: copy html
      template:
        src: index.j2
        dest: /nfs/lnmp2/index.html
    - name: copy php
      template:
        src: index-php.j2
        dest: /nfs/lnmp1/index.php
    - name: start nfs
      service:
        name: nfs-server
        state: started
        enabled: yes
- name: nfs client host1
  hosts: host1
  tasks:
    - name: install nfs
      yum:
        name: nfs-utils
        state: present
    - name: start nfs client
      service:
        name: nfs-idmapd
        state: started
        enabled: yes
    - name: Mount NFS share
      ansible.builtin.mount:
        path: /usr/local/nginx/html/
        src: nfs:/nfs/lnmp1/
        fstype: nfs
        state: mounted
        opts: rw,sync
- name: nfs client host2
  hosts: host2
  tasks:
    - name: install nfs
      yum:
        name: nfs-utils
        state: present
    - name: start nfs client
      service:
        name: nfs-idmapd
        state: started
        enabled: yes
    - name: Mount NFS share
      mount:
        path: /usr/local/nginx/html/
        src: nfs:/nfs/lnmp2/
        fstype: nfs
        state: mounted
        opts: rw,sync
###
```

所需文件：

解压压缩包，将清单修改

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101008732.png)

******

第二题

监控 nginx 进程数

```shell
vim /active
###
#!/bin/bash
CURRENT_PROCESSES=$(ps aux | grep -c '[n]ginx')
echo $CURRENT_PROCESSES
###
chmod 777 /active.sh
vim /etc/zabbix_agentd.conf.d/active.conf
###
UserParameter=nginx_active[*],/active.sh
###
systemctl restart zabbix-agent
# 在监控端查看
zabbix_get  -s 10.15.200.102 -p 10050 -k "nginx_active"
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101026986.png)

配置 zabbix 网页

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101033466.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101034010.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101033897.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101034826.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101035857.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101035026.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101036549.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101036030.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101036663.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101037817.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408101042495.png)
