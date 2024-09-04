创建一台 ecs 服务器

可以使用抢占式实例

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904094201.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904094218.png)

其他设置与第一台服务器相同

在两台 ecs 上安装 nginx，修改端口为 8080

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904094441.png)

启动 nginx

```shell
# 创建网页
# server1
echo zxh_ecs1 > /usr/share/nginx/html/index.html
# server2
echo zxh_ecs2 > /usr/share/nginx/html/index.html
# 访问测试
curl 127.0.0.1
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904094722.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904094724.png)

创建 clb

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904094823.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904094851.png)

使用按量付费 ---> 购买

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095029.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095103.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095106.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095120.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095136.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095205.png)

选择 http 协议
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095249.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904095327.png)
访问 clb 的公网 ip 加端口

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904104240.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240904104242.png)
