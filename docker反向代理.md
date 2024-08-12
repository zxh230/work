要求：
![4d9b786e81f23bc359726250ea42b65.jpg](https://gitee.com/zhaojiedong/img/raw/master/4d9b786e81f23bc359726250ea42b65.jpg)

导入 [nginx-1.24.0. tar. gz](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/nginx-1.24.0.tar.gz) 压缩包

```shell
# 运行rocky9系统镜像
docker run -it --name web1 rocky:9 bash
# 查询scp命令归属
yum provides scp
# 安装命令包，拷贝压缩包到容器内
yum -yq install openssh-clients-8.7p1-38.el9_4.4.x86_64
scp 10.15.200.241:/root/nginx-1.24.0.tar.gz ./
# 安装源码包依赖
yum -yq install zlib-devel pcre-devel openssl openssl-devel gcc
# 解压nginx包并进行源码安装
tar -xf nginx-1.24.0.tar.gz
cd nginx-1.24.0
./configure --prefix=/usr/local/nginx --conf-path=/etc/nginx/nginx.conf --sbin-path=/usr/local/sbin
make -j 4 && make install
# 设置开机自启（可以不做）
echo nginx >> ~/.bashrc
# 退出容器，进行打包
exit
docker start web1
# 后面的镜像名与版本号可以自定义
docker commit nginx web2:zxh
docker export nginx -o web3.tar
docker import web3.tar web3:zxh
# 启动镜像
docker run -itd --name web2 web2:zxh bash
docker run -itd --name web3 web3:zxh bash
# 查看镜像
docekr ps -a
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240812191953.png)

修改网页文件
```shell
docker exec -itd web1 sh -c 'echo "zhaojiedong1" > /usr/local/nginx/html/index.html'
docker exec -itd web2 sh -c 'echo "zhaojiedong2" > /usr/local/nginx/html/index.html'
docker exec -itd web3 sh -c 'echo "zhaojiedong3" > /usr/local/nginx/html/index.html'
# 查看容器IP地址
docker inspect web1 web2 web3 |grep \"IPAddress\"
# 访问测试
curl 172.17.0.2
curl 172.17.0.3
curl 172.17.0.4
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240812193112.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240812193138.png)


配置 nginx 反向代理

```shell
docker run -itd --name nginx nginx:1.24 bash

```