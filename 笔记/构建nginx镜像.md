# 构建nginx镜像

确保存在rockylinux9镜像，是rockylinux9即可
![image-20240712234507555](https://gitee.com/zhaojiedong/img/raw/master/image-20240712234507555.png)

## 开始构建

nginx1.24下载：>[nginx1.24.0](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/nginx-1.24.0.tar.gz)

```shell
mkdir nginx_images/
cd nginx_images/
mv ../nginx-1.24.0.tar.gz ./
vim Dockerfile
###
FROM registry.cn-hangzhou.aliyuncs.com/zxh230/rockylinux:9
RUN yum -y install iproute iputils procps-ng net-tools make gcc zlib-devel pcre-devel pcre zlib openssl openssl-devel 
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

