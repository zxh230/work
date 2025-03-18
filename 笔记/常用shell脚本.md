```shell
date +%F -d '1 days ago'  ## 查看一天之前的日期
```

```shell
for h in $(seq 1 1000) ## 循环1000次
> do
>   mysql -uroot -p'!@#qweASD'69 -e 'select count(*) from 6ecc.hot_movies;'
> sleep 1
> done
######
test -d /data || mkdir /data  ## 查询/data/目录是否存在，如果不存在则创建
```

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

