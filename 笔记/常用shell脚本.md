#### shell 脚本

九九乘法表

```shell
#!/bin/bash
<<mmm
九九乘法表
mmm

for x in {1..9}
do
    for y in $(seq 1 $x)
    do
      echo -ne "$y*$x=$[$y*$x]\t"
    done
    echo
done
```

说明：echo -n 表示不换行输出，-e 表示支持反斜线字符转换 

##### 示例

echo 不加选项，输出如下：

![image-20240702100849536](https://gitee.com/zhaojiedong/img/raw/master/202407021008603.png)

由多行输出

加入选项-n 时，输出如下：

![image-20240702101046129](https://gitee.com/zhaojiedong/img/raw/master/202407021010163.png)

结果为梯度输出，但是\t 没有被转换

加入-t 选项时，输出如下：

![image-20240702101207744](https://gitee.com/zhaojiedong/img/raw/master/202407021012778.png)

结果正常输出

------

#### while 循环

```shell
# 写一个计算1+100累积的脚本
#!/bin/bash
i=1
sum=0
while [ $i -lt 100 ]
do
  sum=$[$sum+$i]
  i=$[$i+1]
done
echo $sum
```

显示输出：

![image-20240702105606608](https://gitee.com/zhaojiedong/img/raw/master/202407021056668.png)

##### while 标准输入

将/etc/passwd 添加行号并重定向生成 file 1. txt

```shell
cat -n /etc/passwd > file1.txt
```

查看生成后的 file 1 文件

![image-20240702120901493](https://gitee.com/zhaojiedong/img/raw/master/202407021209588.png)

每 0.3 秒一次循环列出文件内容

```shell
for h in $(cat file1.txt)
do
echo $h
sleep 0.3
done
```

输出结果：

![image-20240702121322615](https://gitee.com/zhaojiedong/img/raw/master/202407021213663.png)

编写脚本

```shell
#!/bin/bash
cat file1.txt | while read nicaicai
do
        echo $nicaicai
        sleep 0.3
done
```

将 cat file 1. txt 的输出结果给与之后的 for 循环作为标准输入

输出结果：

![image-20240702121549920](https://gitee.com/zhaojiedong/img/raw/master/202407021215969.png)

查找僵尸进程
```shell
#!/bin/bash    
# 查找 Linux 系统中的僵尸进程    
# awk 判断 ps 命令输出的第 8 列为 Z 是,显示该进程的 PID 和进程命令    
ps aux | awk '{if($8 == "Z"){print $2,$11}}'
```

删除某个目录下大小为 0 的文件
```shell
#!/bin/bash    
# 删除某个目录下大小为 0 的文件    
#/var/www/html 为测试目录,脚本会清空该目录下所有 0 字节的文件    
dir="/var/www/html"    
find $dir -type f -size 0 -exec rm -rf {} \;
```

获取本机 MAC 地址
```shell
#!/bin/bash    
# 获取本机 MAC 地址    
ip a s | awk 'BEGIN{print  " 本机MAC地址信息如下:"}/^[0‐9]/{print $2;getline;if($0~/link\/ether/){print $2}}' | grep -v lo:    
# awk 读取 ip 命令的输出,输出结果中如果有以数字开始的行,先显示该行的地 2 列(网卡名称),    
# 接着使用 getline 再读取它的下一行数据,判断是否包含 link/ether    
# 如果保护该关键词,就显示该行的第 2 列(MAC 地址)    
# lo 回环设备没有 MAC,因此将其屏蔽,不显示
```

