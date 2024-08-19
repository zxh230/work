
创建目录：

```shell
mkdir -p /opt/data/registry
# 下载镜像
docker pull registry:2
# 启动容器
docker run -itd -p 5000:5000 --restart always --volume /opt/deta/registry:/var/lib/registry --name registry registry:2 
# 访问
curl 10.15.200.242:5000/v2/_catalog
```

