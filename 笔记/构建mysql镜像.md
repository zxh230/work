导入压缩包
mysql-8.0.38-linux-glibc 2.28-x 86_64. tar. xz

```shell
# 编写Dockerfile
vim Dockerfile
###
FROM rocky:9
RUN dnf -y install xz perl-JSON perl-Data-Dumper libaio numactl
COPY mysql-8.0.38-linux-glibc2.28-x86_64.tar.xz /root/
RUN tar -xf /root/mysql-8.0.38-linux-glibc2.28-x86_64.tar.xz -C /usr/local/ \
    && mv /usr/local/mysql-8.0.38-linux-glibc2.28-x86_64 /usr/local/mysql \
    && ln -s /usr/local/mysql/bin/* /usr/local/bin/
RUN useradd mysql \
    && mkdir /var/lib/mysql /var/run/mysqld /var/log/mysql \
    && chown -R mysql:mysql /var/lib/mysql /var/run/mysqld /var/log/mysql
COPY start_mysql.sh /usr/local/bin/start_mysql.sh
RUN chmod +x /usr/local/bin/start_mysql.sh
EXPOSE 3306
ENTRYPOINT ["/usr/local/bin/start_mysql.sh"]
CMD ["-u", "root", "-p"]
###
# 编写启动识别脚本
vim start_mysql.sh
###
#!/bin/bash
/usr/local/mysql/bin/mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql > /dev/null 2>&1 &
sleep 5
/usr/local/mysql/bin/mysqld --user=mysql --datadir=/var/lib/mysql > /dev/null 2>&1 &
sleep 5
if [ "$1" = "-uroot" ]; then
    exec mysql "$@"
else
    exec sh -c "$1"
fi
###
# 开始构建
docker build -t mysql:8 ./
# 测试登录
docker run -it --name mysql --rm mysql:8 -uroot -p
# 等待mysql初始化完成
# 无密码，直接回车即可进入mysql
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240816211343.png)

也可以支持使用其他命令

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240816212544.png)
