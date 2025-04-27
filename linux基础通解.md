# 1，目录结构
| 目录名称        | 应放置文件的内容                          |
| ----------- | --------------------------------- |
| /boot       | 开机所需文件—内核、开机菜单以及所需配置文件等           |
| /dev        | 以文件形式存放任何设备与接口                    |
| /etc        | 配置文件                              |
| /home       | 用户主目录                             |
| /bin        | 存放单用户模式下还可以操作的命令                  |
| /lib        | 开机时用到的函数库，以及/bin与/sbin下面的命令要调用的函数 |
| /sbin       | 开机过程中需要的命令                        |
| /media      | 用于挂载设备文件的目录                       |
| /opt        | 放置第三方的软件                          |
| /root       | 系统管理员的家目录                         |
| /srv        | 一些网络服务的数据文件目录                     |
| /tmp        | 任何人均可使用的“共享”临时目录                  |
| /proc       | 虚拟文件系统，例如系统内核、进程、外部设备及网络状态等       |
| /usr/local  | 用户自行安装的软件                         |
| /usr/sbin   | Linux系统开机时不会使用到的软件/命令/脚本          |
| /usr/share  | 帮助与说明文件，也可放置共享文件                  |
| /var        | 主要存放经常变化的文件，如日志                   |
| /lost+found | 当文件系统发生错误时，将一些丢失的文件片段存放在这里        |
# 2，帮助命令
想要查看某个命令的帮助信息，可以使用 man 命令。执行 man 命令后，就进入到浏览页面，浏览页面常用按键如下：

| 按键        | 用处                    |
| --------- | --------------------- |
| 空格键       | 向下翻一页                 |
| PaGe down | 向下翻一页                 |
| PaGe up   | 向上翻一页                 |
| home      | 直接前往首页                |
| end       | 直接前往尾页                |
| /         | 从上至下搜索某个关键词，如“/linux” |
| ?         | 从下至上搜索某个关键词，如“?linux” |
| n         | 定位到下一个搜索到的关键词         |
| N         | 定位到上一个搜索到的关键词         |
| q         | 退出帮助文档                |
# 3，yum 相关命令
| 命令                    | 效果             |
| --------------------- | -------------- |
| yum repolist all      | 列出所有仓库         |
| yum list all          | 列出仓库中所有软件包     |
| yum info 软件包名称        | 查看软件包信息        |
| yum install 软件包名称     | 安装软件包          |
| yum reinstall 软件包名称   | 重新安装软件包        |
| yum update 软件包名称      | 升级软件包          |
| yum remove 软件包名称      | 移除软件包          |
| yum clean all         | 清除所有仓库缓存       |
| yum check-update      | 检查可更新的软件包      |
| yum grouplist         | 查看系统中已经安装的软件包组 |
| yum groupinstall 软件包组 | 安装指定的软件包组      |
| yum groupremove 软件包组  | 移除指定的软件包组      |
| yum groupinfo 软件包组    | 查询指定的软件包组信息    |
# 4，服务相关命令
服务的启动、重启、停止、重载、查看状态等常用命令如下：

| System V init 命令（RHEL 6系统） | systemctl命令（RHEL 7 系统）        | 作用              |
| -------------------------- | ----------------------------- | --------------- |
| service foo start          | systemctl start foo.service   | 启动服务            |
| service foo restart        | systemctl restart foo.service | 重启服务            |
| service foo stop           | systemctl stop foo.service    | 停止服务            |
| service foo reload         | systemctl reload foo.service  | 重新加载配置文件（不终止服务） |
| service foo status         | systemctl status foo.service  | 查看服务状态          |

服务开机启动、不启动、查看各级别下服务启动状态等常用命令：

|System V init 命令（RHEL 6系统）|systemctl命令（RHEL 7 系统）|作用|
|---|---|---|
|chkconfig foo in|systemctl enable foo.service|开机自动启动|
|chkconfig foo off|systemctl disable foo.service|开机不自动启动|
|chkconfig foo|systemctl is-enable foo.service|查看特定服务是否为开启自动启动|
|chkconfig --list|systemctl list-unit-files --type=service|查看各个级别下服务的启动与禁用情况|
# 5，系统常用命令
### 1. [echo](https://wangchujiang.com/linux-command/c/echo.html#echo)

echo 命令用于在终端输出字符串或变量提取后的值，格式为：echo [字符串 | $变量] 。

```shell
[root@hadoop001 ~]# echo hello
hello
[root@hadoop001 ~]# echo $JAVA_HOME
/usr/java/jdk1.8.0_201
```

### 2. [date](https://wangchujiang.com/linux-command/c/date.html#date)

date 命令用于显示及设置系统的时间或日期。常用参数如下：

|参数|作用|
|---|---|
|%t|跳格[Tab键]|
|%H|小时（00～23）|
|%I|小时（00～12）|
|%M|分钟（00～59）|
|%S|秒（00～59）|
|%j|今年中的第几天|

按照默认格式查看当前时间：

```shell
[root@hadoop001 ~]# date
2019年 07月 02日 星期二 14:07:34 CST
```

按照“年-月-日 小时:分钟:秒”的格式查看当前系统时间的date命令如下所示：

```shell
[root@hadoop001 ~]# date "+%Y-%m-%d %H:%M:%S"
2019-07-02 14:07:52 
```

设置系统时间：

```shell
[root@hadoop001 ~]# date -s "20190702 14:10:10"
2019年 07月 02日 星期二 14:10:10 CST
```

### 3. [reboot](https://wangchujiang.com/linux-command/c/reboot.html#reboot)

reboot 命令用于重启系统，其格式为 reboot。
#### 选项

```shell
-d：重新开机时不把数据写入记录文件/var/tmp/wtmp。本参数具有“-n”参数效果；
-f：强制重新开机，不调用shutdown指令的功能；
-i：在重开机之前，先关闭所有网络界面；
-n：重开机之前不检查是否有未结束的程序；
-w：仅做测试，并不真正将系统重新开机，只会把重开机的数据写入/var/log目录下的wtmp记录文件。
```
### 4. [poweroff](https://wangchujiang.com/linux-command/c/poweroff.html#poweroff)

poweroff 命令用于关闭系统，其格式为 poweroff。
#### 选项

```shell
-n 关闭之前不同步
-p 当被称为halt时关闭电源
-v 增加输出，包括消息
-q 降低输出错误唯一的消息
-w 并不实际关闭系统，只是写入/var/log/wtmp文件中
-f 强制关机，不调用shutdown
```
### 5. wget

wget 命令用于在终端中下载网络文件，格式为： wget [参数] 下载地址。 常用参数如下：

|参数|作用|
|---|---|
|-b|后台下载模式|
|-P|下载到指定目录|
|-t|最大尝试次数|
|-c|断点续传|
|-p|下载页面内所有资源，包括图片、视频等|
|-r|递归下载|

示例下载百度首页的内容到`/usr/baidu`目录下：

```shell
[root@hadoop001 usr]# wget -r -p www.baidu.com -P /usr/baidu
```

### 6. ps

ps 命令用于查看系统中的进程状态，格式为：ps [参数] ，常用参数如下：

|参数|作用|
|---|---|
|-a|显示所有进程（包括其他用户的进程）|
|-u|用户以及其他详细信息|
|-x|显示没有控制终端的进程|

在 Linux 系统中，有5种常见的进程状态，分别为运行、中断、不可中断、僵死与停止：

- **R (运行)** ：进程正在运行或在运行队列中等待。
- **S (中断)** ：进程处于休眠中，当某个条件形成后或者接收到信号时，则脱离该 状态。
- **D (不可中断)** ：进程不响应系统异步信号，即便用kill命令也不能将其中断。
- **Z (僵死)** ：进程已经终止，但进程描述符依然存在, 直到父进程调用wait4()系统函数后将进程释放。
- **T (停止)** ：进程收到停止信号后停止运行。

示例如下：

```shell
[root@hadoop001 usr]# ps -u
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root      2688  0.0  0.0 110092   856 tty1     Ss+  13:45   0:00 /sbin/agetty --
root      3679  0.0  0.1 115572  2216 pts/0    Ss   13:52   0:00 -bash
root     12471  0.0  0.1 155360  1888 pts/0    R+   14:17   0:00 ps -u
```

|USER|PID|%CPU|%MEM|VSZ|RSS|TTY|STAT|START|TIME|COMMAND|
|---|---|---|---|---|---|---|---|---|---|---|
|进程的所有者|进程ID号|运算器占用率|内存占用率|虚拟内存使用量(单位是KB)|占用的固定内存量(单位是KB)|所在终端|进程状态|被启动的时间|实际使用CPU的时间|命令名称与参数|

### 7. top

top 命令用于动态地监视进程活动与系统负载等信息，其格式为 top。

```shell
top - 14:21:25 up 35 min,  1 user,  load average: 0.00, 0.02, 0.05
Tasks: 104 total,   1 running, 103 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.5 us,  0.7 sy,  0.0 ni, 98.7 id,  0.0 wa,  0.0 hi,  0.2 si,  0.0 st
KiB Mem :  1882148 total,  1316728 free,   203592 used,   361828 buff/cache
KiB Swap:  2097148 total,  2097148 free,        0 used.  1497748 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 3680 root      20   0  113444   1776   1344 S   0.3  0.1   0:06.45 bash
13685 root      20   0  161880   2200   1560 R   0.3  0.1   0:00.09 top
    1 root      20   0  193696   6656   4180 S   0.0  0.4   0:03.10 systemd
```

top 命令执行结果的前5行为系统整体的统计信息，其所代表的含义如下：

**第1行**：系统时间、运行时间、登录终端数、系统负载（三个数值分别为1分钟、5分钟、15分钟内的平均值，数值越小意味着负载越低）。

**第2行**：进程总数、运行中的进程数、睡眠中的进程数、停止的进程数、僵死的进程数。

**第3行**：用户占用资源百分比（us）、系统内核占用资源百分比（sy）、改变过优先级的进程资源百分比（ni）、空闲的资源百分比（id）等。其中数据均为CPU数据并以百分比格式显示，例如 `98.7 id` 意味着有 98.7% 的 CPU 处理器资源处于空闲。

**第4行**：物理内存总量、内存使用量、内存空闲量、作为内核缓存的内存量。

**第5行**：虚拟内存总量、虚拟内存使用量、虚拟内存空闲量、已被提前加载的内存量。

### 8. pidof

pidof 命令用于查询某个指定服务进程的 PID 值，格式为：pidof [参数][服务名称]。

### 9. kill

kill 命令用于终止某个指定 PID 的服务进程，格式为：kill [参数][进程 PID]。

### 10. killall

killall 命令用于终止某个指定名称的服务所对应的全部进程，格式为：killall [参数][服务名称]。