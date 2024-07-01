## nginx动静分离

1. 安装nginx

   - 导入[rpm](https://gitee.com/zhaojiedong/img/raw/master/%E6%96%87%E4%BB%B6/nginx-1.24.0-1.el9.x86_64.rpm)包并安装

   ```shell
   yum -yq localinstall nginx-1.24.0-1.el9.x86_64.rpm
   ```

#### node01

1. 更改配置文件

   ```shell
   vim /etc/nginx/vhosts_www/aaa.conf
   server {
       server_name zhaojiedong.example.cn;
       listen 80;
       root /nginx;
   
       location /static/ {
       index index.html;
       }
       location /invalid/ {
       index index.html;
       }
   }
   ```

2. 解压[网页文件](https://gitee.com/zhaojiedong/img/raw/master/%E6%96%87%E4%BB%B6/nginx.tgz)

   ```shell
   tar -xf nginx.tgz -C /
   ```

3. 启动nginx

   ```shell
   systemctl start nginx
   ```

#### node02

1. 创建配置文件

   ```shell
   vim /etc/nginx/vhosts_www/aaa.conf
   server {
       server_name static.example.cn;
       listen 80;
       root /nginx;
   }
   vim /etc/nginx/vhosts_www/6ecc.conf
   server {
   listen 80;
   root /nginx/static/6ecc/;
   server_name 6ecc.example.cn;
   }
   vim /etc/nginx/vhosts_www/valid.conf
   server {
   server_name valid.cloud.cn;
   listen 80;
   root /nginx/invalid/dt/;
   }
   ```

2. 解压[图片文件](https://gitee.com/zhaojiedong/img/raw/master/%E6%96%87%E4%BB%B6/nginx2.tgz)

   ```shell
   tar -xf nginx2.tgz -C /
   ```

3. 启动nginx

   ```shell
   systemctl start nginx
   ```

------

## windows

写入域名解析（小地球）

username.example.cn 10.15.200.101

6ecc.example.cn 10.15.200.102

valid.cloud.cn 10.15.200.102