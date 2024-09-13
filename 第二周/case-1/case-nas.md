![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904230845.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904230855.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904230947.png)

复制挂载地址

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904231110.png)

使用 nfs 进行挂载

```shell
mount -t nfs [挂载地址]:/ /mnt/
# 查看挂载点
df -Th
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904231251.png)

将 index 页面同步到 nas

```shell
cp /usr/share/nginx/html/index.html /mnt/index-svr1.html
scp 10.0.10.159:/usr/share/nginx/html/index.html /mnt/index-svr2.index
```
