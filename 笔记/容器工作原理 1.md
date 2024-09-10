# 容器工作原理

容器 --> docker -->   

半解耦虚拟化与完全解耦虚拟化

耦合：互相冲突

程序解耦：解决程序间运行时的冲突，需要划分空间

完全解耦状态：VMware提出设想，类似虚拟机结构

半解耦：将重复的库与文件排除，

操作系统：固定的目录结构+内核



Linux上能不能运行windows系统？

 不能，内核不同

那些程序不能运行？

特定内核版本的程序



查看进程pid号

![image-20240704170606065](https://gitee.com/zhaojiedong/img/raw/master/image-20240704170606065.png)

伪文件系统：

/proc/:内存文件在系统中的映射

当程序运行且有pid时，在该目录会有对应的目录

![image-20240704171050934](https://gitee.com/zhaojiedong/img/raw/master/image-20240704171050934.png)

当程序停止，目录也随之消失

![image-20240704171140004](https://gitee.com/zhaojiedong/img/raw/master/image-20240704171140004.png)





/sys/：内核和操作系统在运行时产生的临时映射

NAMESPACE

系统运行：

1. 内核 -> 操作系统 -- 软件 -> shell -> 库文件（ dll/lib库文件，动态链接库）



C-GROUP

