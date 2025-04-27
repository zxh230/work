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
#### 参数
format：输出的时间格式。

```shell
format可用的转义序列如下：

%%      百分号
%a      当地缩写的工作日名称（例如，Sun）
%A      当地完整的工作日名称（例如，Sunday）
%b      当地缩写的月份名称（例如，Jan）
%B      当地完整的月份名称（例如，January）
%c      当地的日期和时间（例如，Thu Mar  3 23:05:25 2005）
%C      世纪，和%Y类似，但是省略后两位（例如，20）
%d      一月中的一天（例如，01）
%D      日期，等价于%m/%d/%y
%e      一月中的一天，格式使用空格填充，等价于%_d
%F      完整的日期；等价于%+4Y-%m-%d
%g      ISO标准计数周的年份的最后两位数字
%G      ISO标准计数周的年份，通常只对%V有用
%h      等价于%b
%H      小时，范围（00..23）
%I      小时，范围（00..23）
%j      一年中的一天，范围（001..366）
%k      小时，使用空格填充，范围（0..23），等价于%_H
%l      小时，使用空格填充，范围（1..12），等价于%_I
%m      月，范围（01..12）
%M      分钟，范围（00..59）
%n      换行符
%N      纳秒，范围（000000000..000000000）
%p      用于表示当地的AM或PM，如果未知则为空白
%P      类似于%p，但用小写表示
%q      季度，范围（1..4）
%r      当地以12小时表示的时钟时间（例如，11:11:04 PM）
%R      24小时每分钟；等价于%H:%M
%s      自协调世界时1970年01月01日00时00分以来的秒数
%S      秒数，范围（00..60）
%t      水平制表符
%T      时间；等价于%H:%M:%S
%u      一周中的一天（1..7），1代表星期一
%U      一年中的第几周，周日作为一周的起始（00..53）
%V      ISO标准计数周，该方法将周一作为一周的起始（01..53）
%w      一周中的一天（0..6），0代表星期天
%W      一年中的第几周，周一作为一周的起始（00..53）
%x      当地的日期表示（例如，12/31/99）
%X      当地的时间表示（例如，23:13:48）
%y      年份后两位数字，范围（00..99）
%Y      年份
%z      +hhmm格式的数值化时区格式（例如，-0400）
%:z     +hh:mm格式的数值化时区格式（例如，-04:00）
%::z    +hh:mm:ss格式的数值化时区格式（例如，-04:00:00）
%:::z   数值化时区格式，相比上一个格式增加':'以显示必要的精度（例如，-04，+05:30）
%Z      时区缩写（如EDT）

默认情况下，日期用零填充数字字段；以下可选的符号可以跟在'%'后面:

-      (连字符) 不要填充相应的字段。
_      (下划线) 使用空格填充相应的字段。
0      (数字0) 使用数字0填充相应的字段。
+      用数字0填充，未来年份大于4位数字则在前面加上'+'号。
^      允许的情况下使用大写。
#      允许的情况下将默认的大写转换为小写，默认的小写转换为大写。

在任何标志之后都有一个可选的字段宽度，如小数；然后是一个可选的修饰符，在可用的情况下，使用E来使用当地语言环境的替代表示，
使用O来使用当地语言环境的替代数字符号。
```
#### 选项

```shell
长选项与短选项等价

-d, --date=STRING          解析字符串并按照指定格式输出，字符串不能是'now'。
--debug                    注释已解析的日期，并将有疑问的用法发送到标准错误。
-f, --file=DATEFILE        类似于--date; 一次从DATEFILE处理一行。
-I[FMT], --iso-8601[=FMT]  按照ISO 8601格式输出，FMT可以为'date'(默认)，'hours'，'minutes'，'seconds'，'ns'。例如：2006-08-14T02:34:56-06:00
-R, --rfc-email            按照RFC 5322格式输出，例如: Mon, 14 Aug 2006 02:34:56 -0600
--rfc-3339=FMT             按照RFC 3339格式输出，FMT可以为'date', 'seconds','ns'中的一个，例如：2006-08-14 02:34:56-06:00
-r, --reference=FILE       显示文件的上次修改时间。
-s, --set=STRING           根据字符串设置系统时间。
-u, --utc, --universal     显示或设置世界协调时(UTC)。
--help                     显示帮助信息并退出。
--version                  显示版本信息并退出。
```

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

**wget命令** 用来从指定的URL下载文件。wget非常稳定，它在带宽很窄的情况下和不稳定网络中有很强的适应性，如果是由于网络的原因下载失败，wget会不断的尝试，直到整个文件下载完毕。如果是服务器打断下载过程，它会再次联到服务器上从停止的地方继续下载。这对从那些限定了链接时间的服务器上下载大文件非常有用。

wget支持HTTP，HTTPS和FTP协议，可以使用HTTP代理。所谓的自动下载是指，wget可以在用户退出系统的之后在后台执行。这意味这你可以登录系统，启动一个wget下载任务，然后退出系统，wget将在后台执行直到任务完成，相对于其它大部分浏览器在下载大量数据时需要用户一直的参与，这省去了极大的麻烦。

用于从网络上下载资源，没有指定目录，下载资源回默认为当前目录。wget虽然功能强大，但是使用起来还是比较简单：

1. **支持断点下传功能** 这一点，也是网络蚂蚁和FlashGet当年最大的卖点，现在，Wget也可以使用此功能，那些网络不是太好的用户可以放心了；
2. **同时支持FTP和HTTP下载方式** 尽管现在大部分软件可以使用HTTP方式下载，但是，有些时候，仍然需要使用FTP方式下载软件；
3. **支持代理服务器** 对安全强度很高的系统而言，一般不会将自己的系统直接暴露在互联网上，所以，支持代理是下载软件必须有的功能；
4. **设置方便简单** 可能，习惯图形界面的用户已经不是太习惯命令行了，但是，命令行在设置上其实有更多的优点，最少，鼠标可以少点很多次，也不要担心是否错点鼠标；
5. **程序小，完全免费** 程序小可以考虑不计，因为现在的硬盘实在太大了；完全免费就不得不考虑了，即使网络上有很多所谓的免费软件，但是，这些软件的广告却不是我们喜欢的。
##### 语法

```shell
wget [参数] [URL地址]
```
#### 选项

```shell
启动参数：

-V, –-version 显示wget的版本后退出
-h, –-help 打印语法帮助
-b, –-background 启动后转入后台执行
-e, –-execute=COMMAND 执行 .wgetrc 格式的命令，wgetrc格式参见/etc/wgetrc或~/.wgetrc

记录和输入文件参数：

-o, –-output-file=FILE 把记录写到FILE文件中
-a, –-append-output=FILE 把记录追加到FILE文件中
-d, –-debug 打印调试输出
-q, –-quiet 安静模式(没有输出)
-v, –-verbose 冗长模式(这是缺省设置)
-nv, –-non-verbose 关掉冗长模式，但不是安静模式
-i, –-input-file=FILE 下载在FILE文件中出现的URLs
-F, –-force-html 把输入文件当作HTML格式文件对待
-B, –-base=URL 将URL作为在-F -i参数指定的文件中出现的相对链接的前缀
–-sslcertfile=FILE 可选客户端证书
–-sslcertkey=KEYFILE 可选客户端证书的KEYFILE
–-egd-file=FILE 指定EGD socket的文件名

下载参数：

–-bind-address=ADDRESS 指定本地使用地址(主机名或IP，当本地有多个IP或名字时使用)
-t, –-tries=NUMBER 设定最大尝试链接次数(0 表示无限制).
-O –-output-document=FILE 把文档写到FILE文件中
-nc, –-no-clobber 不要覆盖存在的文件或使用.#前缀
-c, –-continue 接着下载没下载完的文件
–progress=TYPE 设定进程条标记
-N, –-timestamping 不要重新下载文件除非比本地文件新
-S, –-server-response 打印服务器的回应
–-spider 不下载任何东西
-T, –-timeout=SECONDS 设定响应超时的秒数
-w, –-wait=SECONDS 两次尝试之间间隔SECONDS秒
–waitretry=SECONDS 在重新链接之间等待1…SECONDS秒
–random-wait 在下载之间等待0…2*WAIT秒
-Y, –-proxy=on/off 打开或关闭代理
-Q, –-quota=NUMBER 设置下载的容量限制
-–limit-rate=RATE 限定下载输率

目录参数：

-nd –-no-directories 不创建目录
-x, –-force-directories 强制创建目录
-nH, –-no-host-directories 不创建主机目录
-P, –-directory-prefix=PREFIX 将文件保存到目录 PREFIX/…
–cut-dirs=NUMBER 忽略 NUMBER层远程目录

HTTP 选项参数：

-–http-user=USER 设定HTTP用户名为 USER.
-–http-passwd=PASS 设定http密码为 PASS
-C, –-cache=on/off 允许/不允许服务器端的数据缓存 (一般情况下允许)
-E, –-html-extension 将所有text/html文档以.html扩展名保存
-–ignore-length 忽略 Content-Length 头域
-–header=STRING 在headers中插入字符串 STRING
-–proxy-user=USER 设定代理的用户名为 USER
-–proxy-passwd=PASS 设定代理的密码为 PASS
-–referer=URL 在HTTP请求中包含  Referer: URL 头
-s, –-save-headers 保存HTTP头到文件
-U, –-user-agent=AGENT 设定代理的名称为 AGENT而不是 Wget/VERSION
-–no-http-keep-alive 关闭 HTTP活动链接 (永远链接)
–-cookies=off 不使用 cookies
–-load-cookies=FILE 在开始会话前从文件 FILE中加载cookie
-–save-cookies=FILE 在会话结束后将 cookies保存到 FILE文件中

FTP 选项参数：

-nr, -–dont-remove-listing 不移走 .listing 文件
-g, -–glob=on/off 打开或关闭文件名的 globbing机制
-–passive-ftp 使用被动传输模式 (缺省值).
-–active-ftp 使用主动传输模式
-–retr-symlinks 在递归的时候，将链接指向文件(而不是目录)

递归下载参数：

-r, -–recursive 递归下载－－慎用!
-l, -–level=NUMBER 最大递归深度 (inf 或 0 代表无穷)
–-delete-after 在现在完毕后局部删除文件
-k, –-convert-links 转换非相对链接为相对链接
-K, –-backup-converted 在转换文件X之前，将之备份为 X.orig
-m, –-mirror 等价于 -r -N -l inf -nr
-p, –-page-requisites 下载显示HTML文件的所有图片

递归下载中的包含和不包含(accept/reject)：

-A, –-accept=LIST 分号分隔的被接受扩展名的列表
-R, –-reject=LIST 分号分隔的不被接受的扩展名的列表
-D, –-domains=LIST 分号分隔的被接受域的列表
–-exclude-domains=LIST 分号分隔的不被接受的域的列表
–-follow-ftp 跟踪HTML文档中的FTP链接
–-follow-tags=LIST 分号分隔的被跟踪的HTML标签的列表
-G, –-ignore-tags=LIST 分号分隔的被忽略的HTML标签的列表
-H, –-span-hosts 当递归时转到外部主机
-L, –-relative 仅仅跟踪相对链接
-I, –-include-directories=LIST 允许目录的列表
-X, –-exclude-directories=LIST 不被包含目录的列表
-np, –-no-parent 不要追溯到父目录
wget -S –-spider url 不下载只显示过程
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