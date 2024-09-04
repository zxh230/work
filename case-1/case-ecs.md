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
            index  index.php;
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
# 安装php
yum -yq install php php-cli php-fpm php-mysqlnd php-zip php-gd php-mcrypt php-mbstring php-xml php-pear php-bcmath php-redis php-ldap php-intl php-pecl-imagick php-opcache
# 修改php-fpm配置文件
vim/etc/php-fpm.d/www.conf 
###
[www]
user = nginx
group = nginx
listen = /run/php-fpm/www.sock
listen.owner = nginx
listen.group = nginx
listen.mode = 0660
listen.allowed_clients = 127.0.0.1
pm = dynamic
pm.max_children = 50
pm.start_servers = 5
pm.min_spare_servers = 5
pm.max_spare_servers = 35
slowlog = /var/log/php-fpm/www-slow.log
php_admin_value[error_log] = /var/log/php-fpm/www-error.log
php_admin_flag[log_errors] = on
php_value[session.save_handler] = files
php_value[session.save_path]    = /var/lib/php/session
php_value[soap.wsdl_cache_dir]  = /var/lib/php/wsdlcache
###
# 修改wordpress连接配置
cp /wordpress/wp-config-sample.php /wordpress/wp-config.php
vim /wordpress/wp-config.php
```
```php
define( 'DB_NAME', '阿里云RDS数据库' );
/** Database username */
define( 'DB_USER', '阿里云RDS数据库账号' );
/** Database password */
define( 'DB_PASSWORD', '阿里云RDS数据库密码' );
/** Database hostname */
define( 'DB_HOST', '阿里云RDS数据库内网地址' );
/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );
/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );
###
```
```shell
# 启动nginx与php-fpm
nginx
systemctl start php-fpm
# 访问ECS公网ip/index.php测试
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904213441.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904213523.png)

点击登录

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904213548.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904213650.png)
