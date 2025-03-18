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

