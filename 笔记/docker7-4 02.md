#### docker7-4 02

==配置镜像==

容器实例化：

镜像--半解耦虚拟化

1. 运行容器

   ```shell
   # 学名：实例化
   docker images  # 查询镜像
   docker run [容器名]  # 运行容器
   docker ps 	# 查看正在运行的容器
   docker ps -a # 查看docker中的所有容器
   docker run 
   ```

   IS / 代表结束

   容器生命周期=容器命令生命周期

   前端程序 --> 前台运行 --> 占用终端

   后端程序 --> 后台运行

   ```shell
   # 前端程序 --> 前台运行 --> 占用终端
   # 这些命令可以占用终端，【常用】
   sleep 10
   tail -f 或者 tailf
   top
   # 当有新用户进入系统或者进行安装软件等操作时，message会有相应日志信息
   ```

   ```shell
   # 后端程序 --> 后台运行 & / fg
   # 使**分开
   docker run -d centos:9 sleep 1d
   # -d 使宿主机终端和容器终端分开
   ```

   ![image-20240704140228523](https://gitee.com/zhaojiedong/img/raw/master/image-20240704140228523.png)

   输出容器id号

   

   容器中运行的指令必须在镜像中存在

   ![image-20240704140430604](https://gitee.com/zhaojiedong/img/raw/master/image-20240704140430604.png)

   查看运行的shell

   ![image-20240704140617947](https://gitee.com/zhaojiedong/img/raw/master/image-20240704140617947.png)

   可以在终端运行多个shell终端

   ![image-20240704140704461](https://gitee.com/zhaojiedong/img/raw/master/image-20240704140704461.png)

   可以使用exit退出shell

   

   查看某个用户使用的shell

   打开/etc/passwd

   看到用户zxh运行的shell是/bin/bash

   ![image-20240704140932788](https://gitee.com/zhaojiedong/img/raw/master/image-20240704140932788.png)

   

   

   ```shell
   # -itd：i[交互式] -t [tty虚拟终端] -d[使宿主机终端和终端分开]
   # --name 指定容器名
   # bash 要在容器中运行的命令
   docker run -itd --name devtest rocky:9 bash
   ```

   

   ![image-20240704141308185](https://gitee.com/zhaojiedong/img/raw/master/image-20240704141308185.png)

   

   

   ![image-20240704143641831](https://gitee.com/zhaojiedong/img/raw/master/image-20240704143641831.png)

   ```shell
   docker rm [容器名/容器id]  # 删除容器
   # 容器操作 以下所有操作均可以使用容器名或者容器id
   # 但是！当运行的容器名重复时，容器名不可用！
   docker stop af0bda709373			# 停止容器
   docker kill vigilant_yang			# 杀死正在运行的容器
   docker restart vigilant_yang		# 重启容器
   docker start rocky:9				# 运行容器
   docker pause vigilant_yang			# 挂起容器
   docker unpause vigilant_yang		# 接触挂起容器
   docker rm -f $(docker ps -qa)		# 删除所有容器
   ```

   ![image-20240704142241714](https://gitee.com/zhaojiedong/img/raw/master/image-20240704142241714.png)

2. ```shell
   # 运行镜像,指定容器名web，
   docker run -itd --name web --hostname deveb rocky:9
   # 进入容器
   docker attach web
   # 退出容器
   exit
   # 查看容器运行状态
   docker ps -a 
   ```

   ![image-20240704144316715](https://gitee.com/zhaojiedong/img/raw/master/image-20240704144316715.png)

   ```shell
   # 看到一旦退出容器，容器就会被关闭
   # 重新运行容器web
   docker start web
   # exec 表示要在容器内运行命令
   
   docker exec web ls /etc
   # 在容器内再运行一个bash终端
   docker exec -it web bash
   
   <<###
   当在容器内开启超过一个bash/shell终端时，进入容器后exit时，因为存在多个bash/shell，exit退出容器时并不会关闭容器
   ###
   ```

   ![image-20240704145101326](https://gitee.com/zhaojiedong/img/raw/master/image-20240704145101326.png)

   

3. 发现容器内没有ifconfig命令

   ![image-20240704143912721](https://gitee.com/zhaojiedong/img/raw/master/image-20240704143912721.png)

   安装命令包

   ```shell
   # 查询ifoconfig属于哪个软件包
   dnf provides ifocnfig
   dnf install net-tools -y
   # 安装后可以使用ifconfig命令
   ifconfig
   ```



在容器中配置nginx-1.24

```shell
# 进入容器
docker exec -it web bash
# 安装命令scp需要的软件包
dnf install openssh-clients-8.7p1-38.el9_4.1.x86_64
# 将宿主机的nginx软件包导入
scp root@127.17.0.1:/root/nginx-1.24.0.tar.gz .
# 安装依赖同时源码安装
dnf install zlib zlib-devel pcre-devel gcc make
./configure && make && make install
# 启动ngin并修改网页文件
/usr/local/nginx/sbin/nginx
echo helloworld > /usr/local/nginx/html/index.html
# 退出
exit
# 查看容器ip信息
docker inspect web |grep -i ipadd
# 将配置好的web容器打包为镜像
docker commit web zxh_nginx
# sh -c可以将命令作为整体输出，/usr/local/nginx/sbin/nginx启动nginx
docker run -itd --name web2 zxh_nginx sh -c"/usr/local/nginx/bin/nginx; sleep 10"
```

当容器内无法访问外网时

查看

![image-20240704151226324](https://gitee.com/zhaojiedong/img/raw/master/image-20240704151226324.png)

=1时运行外部流量



```shell
# 查看镜像分层，镜像种类不同，层数有多有少
docker history rocky:9
# 一般镜像中都含有CMD层
```

![image-20240704155211364](https://gitee.com/zhaojiedong/img/raw/master/image-20240704155211364.png)

```shell
# 将容器web导出为文件web.tar
# 导出的文件又叫做模板文件
docker export -o web.tar web
# 将文件web.tar导入为镜像web10
docker import web.tar web10
# 导入的镜像默认没有CMD层
```

![image-20240704155848016](https://gitee.com/zhaojiedong/img/raw/master/image-20240704155848016.png)



