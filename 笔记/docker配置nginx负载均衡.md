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

```