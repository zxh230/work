设置阿里云 ecs 硬盘在线扩容，快照

快照
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904175645.png)

硬盘扩容

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904175734.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904175813.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904175843.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904175941.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904175951.png)

硬盘扩容完成

自定义镜像

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904180049.png)

选择自定义镜像

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904180135.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904180148.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904180153.png)

创建弹性伸缩组

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904180853.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904180822.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904180950.png)

配置 lnmp 安装 wordpress

```shell
# 源码编译nginx
# 官网下载wordpress压缩包
# 解压
unzip wordpress-6.6.1.zip 
# 修改nginx配置文件
vim /etc/nginx/nginx.conf
###
user nginx;
worker_processes  1;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    server {
        listen       80;
        server_name  localhost;
        location / {
            root   html;
            index  index.html index.htm;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
        location ~ \.php$ {
            root           /wordpress/;
            fastcgi_pass   unix:/run/php-fpm/www.sock;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  $request_filename;
            include        fastcgi_params;
        }
    }
}
###
# 修改php-fpm配置文件


```