redis负载更新

主机名：node01~node08

已经事前做好 ssh 免密登录

1，在node01~node06上安装redis

```shell
for h in node0{1..6}
do
	ssh -q $h 'yum -y install redis'
done
```

2，在node01上修改配置文件

```shell
egrep '^bind|^cluster' redis.conf 
	bind 0.0.0.0 -::1
	cluster-enabled yes
	cluster-config-file cluster_info_6379.conf
## 上面是已经修改好的配置文件
for h in node0{2..6}
do
	scp /etc/redis/redis.conf $h:/etc/redis/redis.conf
done
```

3，启动服务

```shell
for h in node0{1..6}
do
	ssh -q $h 'systemctl start redis'
done
```

4，在node01上创建集群

```shell
redis-cli --cluster create 10.15.200.101:6379 10.15.200.102:6379 10.15.200.103:6379 10.15.200.104:6379 10.15.200.105:6379 10.15.200.106:6379 --cluster-replicas 1
```

5，写入数据

```shell
for i in `seq 1 100`
do
    echo "hello_world_v1_$i" | redis-cli -c -p 6379 -h 10.15.200.101 -x set "mykey_v1_$i"
done
```

6，查看数据分布情况以及是否成功写入

```shell
 redis-cli --cluster info 10.15.200.101:6379
```

7，将node07作为主节点添加到集群中

```shell
redis-cli --cluster add-node 10.15.200.107:6379 10.15.200.101:6379
```

8，迁移插槽

```shell
 redis-cli --cluster reshard 10.15.200.101:6379
```

![image-20240507092438262](https://gitee.com/zhaojiedong/img/raw/master/202405070935700.png)

迁移节点数为4096

![image-20240507092613648](https://gitee.com/zhaojiedong/img/raw/master/202405070935701.png)

在node07上查询ID

```shell
redis-cli --cluster check 10.15.200.107:6379
```

![image-20240507092727335](https://gitee.com/zhaojiedong/img/raw/master/202405070935702.png)

\# 如图所示，8393318f88f547e8c14c0dd40560ae712cc53737为node07的reids ID

![image-20240507092844108](https://gitee.com/zhaojiedong/img/raw/master/202405070935703.png)

输入ID后移动选项输入all

9，确认插槽分布情况

```shell
redis-cli --cluster info 10.15.200.101:6379
```

![image-20240507093021361](https://gitee.com/zhaojiedong/img/raw/master/202405070935704.png)

发现node07成功加入集群，但是没有从节点

10，为node07添加从节点

```shell
redis-cli --cluster add-node 10.15.200.108:6379 10.15.200.107:6379 --cluster-slave --cluster-master-id 8393318f88f547e8c14c0dd40560ae712cc53737
```

再次查询发现node07已经有了从节点

![image-20240507093405691](https://gitee.com/zhaojiedong/img/raw/master/202405070935705.png)

------

<center>移除节点</center>

查询现有节点

```shell
redis-cli --cluster info 10.15.200.101:6379
```

![image-20240507093405691](https://gitee.com/zhaojiedong/img/raw/master/202405070935705.png)

#### 移除node01及其从节点

1. 移除node01的从节点

   ![image-20240507095718435](https://gitee.com/zhaojiedong/img/raw/master/202405070957480.png)

   发现node01的从节点为node05

   ```shell
   redis-cli --cluster del-node 10.15.200.101:6379 d79dd9f2d5f8a80be4c3bc2eadbe098bd1e81d0a
   ```

   删除集群中的node05

2. 此时删除node01发现无法删除

   ![image-20240507100004487](https://gitee.com/zhaojiedong/img/raw/master/202405071000515.png)

   \## 因为node01节点上的插槽中存有数据所以无法删除

3. 转移node01的插槽数据

   ```shell
   redis-cli --cluster reshard 10.15.200.101:6379
   ```

   ![image-20240507100306925](https://gitee.com/zhaojiedong/img/raw/master/202405071003954.png)

   转移插槽为4096

   转移的节点id为node01的节点id

   转移源id为node01节点id

4. 验证发现node01数据已经被转移

   ```shell
   redis-cli --cluster info 10.15.200.103:6379
   ```

   ![image-20240507100530945](https://gitee.com/zhaojiedong/img/raw/master/202405071005970.png)

5. 将node01节点移出集群

   ```shell
   redis-cli --cluster del-node 10.15.200.103:6379 0d37488069676612a81249a40a2625b9b5a89673
   ```

6. 均分集群内的数据

   均分前：

   ​		![image-20240507100711949](https://gitee.com/zhaojiedong/img/raw/master/202405071007971.png)

   ```shell
   redis-cli --cluster rebalance 10.15.200.102:6379
   ```

   均分后：

   ​		![image-20240507100844586](https://gitee.com/zhaojiedong/img/raw/master/202405071008609.png)