要求：

client 访物理机的 80 端口，轮训访问 containerA，B.
1、contaier-praxy 为代理服务器映射 HOST 主机内的 80 端口
要求 nginx. conf 文件从HOST 主机内映射，不要进入容器内配置。
容器内无法修改 nginx. conf 文件

2、containerA，B、C 轮训访问
index. html 文件从 HOST 主机内使用 volume 方式映射，
不要进入容器内修改，显示内容为自己名字的拼音

```shell
# 创建目录
mkdir proxy_nginx
cd proxy_nginx
# 创建nginx反向代理文件
vim nginx.conf
### 将10.15.200.241的IP地址更改为自己的物理机IP，端口不变
worker_processes  1;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    upstream wwwbackend {
        server 10.15.200.241:8081 weight=1;
        server 10.15.200.241:8082 weight=1;
        server 10.15.200.241:8083 weight=1;
    }
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
    }
    server {
        listen       80;
        server_name  10.15.200.241;
        location / {
            proxy_pass http://wwwbackend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
###
# 启动容器，nginx.conf路径要正确
docker run -itd --name proxy_nginx -v /root/homework/proxy_nginx/nginx.conf:/usr/local/nginix/conf/nginx.conf:ro -p 80:80 nginx:zxh
# 检查容器是否正常运行
docker ps
# 查看是否为Up状态
# 启动后端节点并挂载网页文件

```