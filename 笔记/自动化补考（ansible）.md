修改主机名

启动 gw 主机

```shell
vim  /etc/dhcp/dhcpd.conf
# 修改主机名
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091730962.png)

修改 dns 服务配置

/var/named/example. cn. zone 

修改对应 ip 的主机名

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091732490.png)

/var/named/200.15.10. in-addr. arpa

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091732176.png)

重启 dhcpd 与 named

`systemctl restart named.service dhcpd.service `

开启虚拟机：

zabbixserver（原 node 01）

host 1 (原 node 02)

host 2（原 node 03）

nfs（原 node 04）

验证主机名是否被修改

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736369.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736891.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736927.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408091736860.png)

******

开始实验：

zabbix
```shell
# 编写部署lnmp

```