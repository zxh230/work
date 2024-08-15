确保存在rockylinux9镜像，是rockylinux9即可
![image-20240712234507555](https://gitee.com/zhaojiedong/img/raw/master/image-20240712234507555.png)

## 开始构建

nginx1.24下载：>[nginx1.24.0](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/nginx-1.24.0.tar.gz)

构建 base 镜像
```shell
vim Dockerfile
###
FROM rocky:9
RUN yum -y install iproute iputils procps-ng net-tools make gcc zlib-devel pcre-devel pcre zlib openssl openssl-devel
CMD ["/bin/bash"]
###
# 开始构建
docker build -t zhaojiedong ./
```

构建 nginx 镜像
```shell
# 导入nginx-1.24压缩包
vim Dockerfile
### 最后一个RUN部分echo后面可以更改为自己的姓名或随意
FROM zhaojiedong:latest
ADD nginx-1.24.0.tar.gz /
WORKDIR /nginx-1.24.0
RUN ./configure --prefix=/usr/local/nginx --sbin-path=/usr/sbin && make && make install
RUN /usr/sbin/nginx
WORKDIR /
EXPOSE 80/tcp
RUN echo zhaojiedong > /usr/local/nginx/html/index.html
CMD ["nginx","-g","daemon off;"]
###
# 开始构建
docker build -t nginx0710:v1.0 ./
# 构建完成后结束
```

启动
```shell
# 启动镜像，--restart always可不加，此选项为容器故障后自动重启
docker run -itd --name web1 --restart always nginx0710:v1.0
docker run -itd --name web2 --restart always nginx0710:v1.0
docker run -itd --name web3 --restart always nginx0710:v1.0
# 访问
curl 172.17.0.2
curl 172.17.0.3
curl 172.17.0.4
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240815172335.png)

