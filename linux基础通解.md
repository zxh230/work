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
#### 选项

```shell
-a：显示所有终端机下执行的程序，除了阶段作业领导者之外。
a：显示现行终端机下的所有程序，包括其他用户的程序。
-A：显示所有程序。
-c：显示CLS和PRI栏位。
c：列出程序时，显示每个程序真正的指令名称，而不包含路径，选项或常驻服务的标示。
-C<指令名称>：指定执行指令的名称，并列出该指令的程序的状况。
-d：显示所有程序，但不包括阶段作业领导者的程序。
-e：此选项的效果和指定"A"选项相同。
e：列出程序时，显示每个程序所使用的环境变量。
-f：显示UID,PPIP,C与STIME栏位。
f：用ASCII字符显示树状结构，表达程序间的相互关系。
-g<群组名称>：此选项的效果和指定"-G"选项相同，当亦能使用阶段作业领导者的名称来指定。
g：显示现行终端机下的所有程序，包括群组领导者的程序。
-G<群组识别码>：列出属于该群组的程序的状况，也可使用群组名称来指定。
h：不显示标题列。
-H：显示树状结构，表示程序间的相互关系。
-j或j：采用工作控制的格式显示程序状况。
-l或l：采用详细的格式来显示程序状况。
L：列出栏位的相关信息。
-m或m：显示所有的执行绪。
n：以数字来表示USER和WCHAN栏位。
-N：显示所有的程序，除了执行ps指令终端机下的程序之外。
-p<程序识别码>：指定程序识别码，并列出该程序的状况。
p<程序识别码>：此选项的效果和指定"-p"选项相同，只在列表格式方面稍有差异。
r：只列出现行终端机正在执行中的程序。
-s<阶段作业>：指定阶段作业的程序识别码，并列出隶属该阶段作业的程序的状况。
s：采用程序信号的格式显示程序状况。
S：列出程序时，包括已中断的子程序资料。
-t<终端机编号>：指定终端机编号，并列出属于该终端机的程序的状况。
t<终端机编号>：此选项的效果和指定"-t"选项相同，只在列表格式方面稍有差异。
-T：显示现行终端机下的所有程序。
-u<用户识别码>：此选项的效果和指定"-U"选项相同。
u：以用户为主的格式来显示程序状况。
-U<用户识别码>：列出属于该用户的程序的状况，也可使用用户名称来指定。
U<用户名称>：列出属于该用户的程序的状况。
v：采用虚拟内存的格式显示程序状况。
-V或V：显示版本信息。
-w或w：采用宽阔的格式来显示程序状况。　
x：显示所有程序，不以终端机来区分。
X：采用旧式的Linux i386登陆格式显示程序状况。
-y：配合选项"-l"使用时，不显示F(flag)栏位，并以RSS栏位取代ADDR栏位　。
-<程序识别码>：此选项的效果和指定"p"选项相同。
--cols<每列字符数>：设置每列的最大字符数。
--columns<每列字符数>：此选项的效果和指定"--cols"选项相同。
--cumulative：此选项的效果和指定"S"选项相同。
--deselect：此选项的效果和指定"-N"选项相同。
--forest：此选项的效果和指定"f"选项相同。
--headers：重复显示标题列。
--help：在线帮助。
--info：显示排错信息。
--lines<显示列数>：设置显示画面的列数。
--no-headers：此选项的效果和指定"h"选项相同，只在列表格式方面稍有差异。
--group<群组名称>：此选项的效果和指定"-G"选项相同。
--Group<群组识别码>：此选项的效果和指定"-G"选项相同。
--pid<程序识别码>：此选项的效果和指定"-p"选项相同。
--rows<显示列数>：此选项的效果和指定"--lines"选项相同。
--sid<阶段作业>：此选项的效果和指定"-s"选项相同。
--tty<终端机编号>：此选项的效果和指定"-t"选项相同。
--user<用户名称>：此选项的效果和指定"-U"选项相同。
--User<用户识别码>：此选项的效果和指定"-U"选项相同。
--version：此选项的效果和指定"-V"选项相同。
--widty<每列字符数>：此选项的效果和指定"-cols"选项相同。
```

#### 举例 ：

```shell
ps axo pid,comm,pcpu # 查看进程的PID、名称以及CPU 占用率
ps aux | sort -rnk 4 # 按内存资源的使用量对进程进行排序
ps aux | sort -nk 3  # 按 CPU 资源的使用量对进程进行排序
ps -A # 显示所有进程信息
ps -u root # 显示指定用户信息
ps -efL # 查看线程数
ps -e -o "%C : %p :%z : %a"|sort -k5 -nr # 查看进程并按内存使用大小排列
ps -ef # 显示所有进程信息，连同命令行
ps -ef | grep ssh # ps 与grep 常用组合用法，查找特定进程
ps -C nginx # 通过名字或命令搜索进程
ps aux --sort=-pcpu,+pmem # CPU或者内存进行排序,-降序，+升序
ps -f --forest -C nginx # 用树的风格显示进程的层次关系
ps -o pid,uname,comm -C nginx # 显示一个父进程的子进程
ps -e -o pid,uname=USERNAME,pcpu=CPU_USAGE,pmem,comm # 重定义标签
ps -e -o pid,comm,etime # 显示进程运行的时间
ps -aux | grep named # 查看named进程详细信息
ps -o command -p 91730 | sed -n 2p # 通过进程id获取服务名称
```

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
#### 选项

```shell
-b：以批处理模式操作；
-c：显示完整的治命令；
-d：屏幕刷新间隔时间；
-I：忽略失效过程；
-s：保密模式；
-S：累积模式；
-i<时间>：设置间隔时间；
-u<用户名>：指定用户名；
-p<进程号>：指定进程；
-n<次数>：循环显示的次数；
-H：所有线程占用资源情况。
```
#### top交互命令

在top命令执行过程中可以使用的一些交互命令。这些命令都是单字母的，如果在命令行中使用了-s选项， 其中一些命令可能会被屏蔽。

```shell
h：显示帮助画面，给出一些简短的命令总结说明；
k：终止一个进程；
i：忽略闲置和僵死进程，这是一个开关式命令；
q：退出程序；
r：重新安排一个进程的优先级别；
S：切换到累计模式；
s：改变两次刷新之间的延迟时间（单位为s），如果有小数，就换算成ms。输入0值则系统将不断刷新，默认值是5s；
f或者F：从当前显示中添加或者删除项目；
o或者O：改变显示项目的顺序；
l：切换显示平均负载和启动时间信息；
m：切换显示内存信息；
t：切换显示进程和CPU状态信息；
c：切换显示命令名称和完整命令行；
M：根据驻留内存大小进行排序；
P：根据CPU使用百分比大小进行排序；
T：根据时间/累计时间进行排序；
w：将当前设置写入~/.toprc文件中。
```
#### 实例

```shell
top - 09:44:56 up 16 days, 21:23,  1 user,  load average: 9.59, 4.75, 1.92
Tasks: 145 total,   2 running, 143 sleeping,   0 stopped,   0 zombie
Cpu(s): 99.8%us,  0.1%sy,  0.0%ni,  0.2%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st
Mem:   4147888k total,  2493092k used,  1654796k free,   158188k buffers
Swap:  5144568k total,       56k used,  5144512k free,  2013180k cached
```

**解释：**

- top - 09:44:56[当前系统时间],
- 16 days[系统已经运行了16天],
- 1 user[个用户当前登录],
- load average: 9.59, 4.75, 1.92[系统负载，即任务队列的平均长度]
- Tasks: 145 total[总进程数],
- 2 running[正在运行的进程数],
- 143 sleeping[睡眠的进程数],
- 0 stopped[停止的进程数],
- 0 zombie[冻结进程数],
- Cpu(s): 99.8%us[用户空间占用CPU百分比],
- 0.1%sy[内核空间占用CPU百分比],
- 0.0%ni[用户进程空间内改变过优先级的进程占用CPU百分比],
- 0.2%id[空闲CPU百分比], 0.0%wa[等待输入输出的CPU时间百分比],
- 0.0%hi[],
- 0.0%st[],
- Mem: 4147888k total[物理内存总量],
- 2493092k used[使用的物理内存总量],
- 1654796k free[空闲内存总量],
- 158188k buffers[用作内核缓存的内存量]
- Swap:  5144568k total[交换区总量],
- 56k used[使用的交换区总量],
- 5144512k free[空闲交换区总量],
- 2013180k cached[缓冲的交换区总量],
### 8. pidof

pidof 命令用于查询某个指定服务进程的 PID 值，格式为：pidof [参数][服务名称]。
#### 选项

```shell
-s：仅返回一个进程号；
-c：仅显示具有相同“root”目录的进程；
-x：显示由脚本开启的进程；
-o：指定不显示的进程ID。
```
### 9. kill

kill 命令用于终止某个指定 PID 的服务进程，格式为：kill [参数][进程 PID]。

### 10. killall

killall 命令用于终止某个指定名称的服务所对应的全部进程，格式为：killall [参数][服务名称]。
#### 选项

```shell
-e：对长名称进行精确匹配；
-l：忽略大小写的不同；
-p：杀死进程所属的进程组；
-i：交互式杀死进程，杀死进程前需要进行确认；
-l：打印所有已知信号列表；
-q：如果没有进程被杀死。则不输出任何信息；
-r：使用正规表达式匹配要杀死的进程名称；
-s：用指定的进程号代替默认信号“SIGTERM”；
-u：杀死指定用户的进程。
```

### 11. awk
文本和数据进行处理的编程语言

**awk** 是一种编程语言，用于在linux/unix下对文本和数据进行处理。数据可以来自标准输入(stdin)、一个或多个文件，或其它命令的输出。它支持用户自定义函数和动态正则表达式等先进功能，是linux/unix下的一个强大编程工具。它在命令行中使用，但更多是作为脚本来使用。awk有很多内建的功能，比如数组、函数等，这是它和C语言的相同之处，灵活性是awk最大的优势。

#### awk命令格式和选项

**语法形式**

```shell
awk [options] 'script' var=value file(s)
awk [options] -f scriptfile var=value file(s)
```

**常用命令选项**

- **-F fs** fs指定输入分隔符，fs可以是字符串或正则表达式，如-F:，默认的分隔符是连续的空格或制表符
- **-v var=value** 赋值一个用户定义变量，将外部变量传递给awk
- **-f scripfile** 从脚本文件中读取awk命令
- **-m[fr] val** 对val值设置内在限制，-mf选项限制分配给val的最大块数目；-mr选项限制记录的最大数目。这两个功能是Bell实验室版awk的扩展功能，在标准awk中不适用。

#### awk模式和操作

awk脚本是由模式和操作组成的。

#### 模式

模式可以是以下任意一个：

- /正则表达式/：使用通配符的扩展集。
- 关系表达式：使用运算符进行操作，可以是字符串或数字的比较测试。
- 模式匹配表达式：用运算符`~`（匹配）和`!~`（不匹配）。
- BEGIN语句块、pattern语句块、END语句块：参见awk的工作原理
#### 操作

操作由一个或多个命令、函数、表达式组成，之间由换行符或分号隔开，并位于大括号内，主要部分是：

- 变量或数组赋值
- 输出命令
- 内置函数
- 控制流语句
#### awk脚本基本结构
```shell
awk 'BEGIN{ print "start" } pattern{ commands } END{ print "end" }' file
```
一个awk脚本通常由：BEGIN语句块、能够使用模式匹配的通用语句块、END语句块3部分组成，这三个部分是可选的。任意一个部分都可以不出现在脚本中，脚本通常是被 **单引号** 中，例如：
```shell
awk 'BEGIN{ i=0 } { i++ } END{ print i }' filename
```
#### awk的工作原理
```shell
awk 'BEGIN{ commands } pattern{ commands } END{ commands }'
```
- 第一步：执行`BEGIN{ commands }`语句块中的语句；
- 第二步：从文件或标准输入(stdin)读取一行，然后执行`pattern{ commands }`语句块，它逐行扫描文件，从第一行到最后一行重复这个过程，直到文件全部被读取完毕。
- 第三步：当读至输入流末尾时，执行`END{ commands }`语句块。

**BEGIN语句块** 在awk开始从输入流中读取行 **之前** 被执行，这是一个可选的语句块，比如变量初始化、打印输出表格的表头等语句通常可以写在BEGIN语句块中。

**END语句块** 在awk从输入流中读取完所有的行 **之后** 即被执行，比如打印所有行的分析结果这类信息汇总都是在END语句块中完成，它也是一个可选语句块。

**pattern语句块** 中的通用命令是最重要的部分，它也是可选的。如果没有提供pattern语句块，则默认执行`{ print }`，即打印每一个读取到的行，awk读取的每一行都会执行该语句块。

**示例**

```shell
echo -e "A line 1\nA line 2" | awk 'BEGIN{ print "Start" } { print } END{ print "End" }'
Start
A line 1
A line 2
End
```

当使用不带参数的`print`时，它就打印当前行，当`print`的参数是以逗号进行分隔时，打印时则以空格作为定界符。在awk的print语句块中双引号是被当作拼接符使用，例如：

```shell
echo | awk '{ var1="v1"; var2="v2"; var3="v3"; print var1,var2,var3; }' 
v1 v2 v3
```

双引号拼接使用：

```shell
echo | awk '{ var1="v1"; var2="v2"; var3="v3"; print var1"="var2"="var3; }'
v1=v2=v3
```

{ }类似一个循环体，会对文件中的每一行进行迭代，通常变量初始化语句（如：i=0）以及打印文件头部的语句放入BEGIN语句块中，将打印的结果等语句放在END语句块中。

#### awk内置变量（预定义变量）

说明：[A][N][P][G]表示第一个支持变量的工具，[A]=awk、[N]=nawk、[P]=POSIXawk、[G]=gawk

```shell
 **$n**  当前记录的第n个字段，比如n为1表示第一个字段，n为2表示第二个字段。 
 **$0**  这个变量包含执行过程中当前行的文本内容。
[N]  **ARGC**  命令行参数的数目。
[G]  **ARGIND**  命令行中当前文件的位置（从0开始算）。
[N]  **ARGV**  包含命令行参数的数组。
[G]  **CONVFMT**  数字转换格式（默认值为%.6g）。
[P]  **ENVIRON**  环境变量关联数组。
[N]  **ERRNO**  最后一个系统错误的描述。
[G]  **FIELDWIDTHS**  字段宽度列表（用空格键分隔）。
[A]  **FILENAME**  当前输入文件的名。
[P]  **FNR**  同NR，但相对于当前文件。
[A]  **FS**  字段分隔符（默认是任何空格）。
[G]  **IGNORECASE**  如果为真，则进行忽略大小写的匹配。
[A]  **NF**  表示字段数，在执行过程中对应于当前的字段数。
[A]  **NR**  表示记录数，在执行过程中对应于当前的行号。
[A]  **OFMT**  数字的输出格式（默认值是%.6g）。
[A]  **OFS**  输出字段分隔符（默认值是一个空格）。
[A]  **ORS**  输出记录分隔符（默认值是一个换行符）。
[A]  **RS**  记录分隔符（默认是一个换行符）。
[N]  **RSTART**  由match函数所匹配的字符串的第一个位置。
[N]  **RLENGTH**  由match函数所匹配的字符串的长度。
[N]  **SUBSEP**  数组下标分隔符（默认值是34）。
```

转义序列

```
\\ \自身
\$ 转义$
\t 制表符
\b 退格符
\r 回车符
\n 换行符
\c 取消换行
```

**示例**

```shell
echo -e "line1 f2 f3\nline2 f4 f5\nline3 f6 f7" | awk '{print "Line No:"NR", No of fields:"NF, "$0="$0, "$1="$1, "$2="$2, "$3="$3}' 
Line No:1, No of fields:3 $0=line1 f2 f3 $1=line1 $2=f2 $3=f3
Line No:2, No of fields:3 $0=line2 f4 f5 $1=line2 $2=f4 $3=f5
Line No:3, No of fields:3 $0=line3 f6 f7 $1=line3 $2=f6 $3=f7
```

使用`print $NF`可以打印出一行中的最后一个字段，使用`$(NF-1)`则是打印倒数第二个字段，其他以此类推：

```shell
echo -e "line1 f2 f3\n line2 f4 f5" | awk '{print $NF}'
f3
f5
echo -e "line1 f2 f3\n line2 f4 f5" | awk '{print $(NF-1)}'
f2
f4
```

打印每一行的第二和第三个字段：

```shell
awk '{ print $2,$3 }' filename
```

统计文件中的行数：

```shell
awk 'END{ print NR }' filename
```

以上命令只使用了END语句块，在读入每一行的时，awk会将NR更新为对应的行号，当到达最后一行NR的值就是最后一行的行号，所以END语句块中的NR就是文件的行数。

一个每一行中第一个字段值累加的例子：

```shell
seq 5 | awk 'BEGIN{ sum=0; print "总和：" } { print $1"+"; sum+=$1 } END{ print "等于"; print sum }' 
总和：
1+
2+
3+
4+
5+
等于
15
```

#### 将外部变量值传递给awk

借助 **`-v`选项** ，可以将外部值（并非来自stdin）传递给awk：

```shell
VAR=10000
echo | awk -v VARIABLE=$VAR '{ print VARIABLE }'
```

另一种传递外部变量方法：

```shell
var1="aaa"
var2="bbb"
echo | awk '{ print v1,v2 }' v1=$var1 v2=$var2
```

当输入来自于文件时使用：

```shell
awk '{ print v1,v2 }' v1=$var1 v2=$var2 filename
```

以上方法中，变量之间用空格分隔作为awk的命令行参数跟随在BEGIN、{}和END语句块之后。

#### 查找进程pid

```shell
netstat -antup | grep 7770 | awk '{ print $NF NR}' | awk '{ print $1}'
```

#### awk运算与判断

作为一种程序设计语言所应具有的特点之一，awk支持多种运算，这些运算与C语言提供的基本相同。awk还提供了一系列内置的运算函数（如log、sqr、cos、sin等）和一些用于对字符串进行操作（运算）的函数（如length、substr等等）。这些函数的引用大大的提高了awk的运算功能。作为对条件转移指令的一部分，关系判断是每种程序设计语言都具备的功能，awk也不例外，awk中允许进行多种测试，作为样式匹配，还提供了模式匹配表达式~（匹配）和!~（不匹配）。作为对测试的一种扩充，awk也支持用逻辑运算符。
#### 算术运算符

| 运算符   | 描述            |
| ----- | ------------- |
| + -   | 加，减           |
| * / & | 乘，除与求余        |
| + - ! | 一元加，减和逻辑非     |
| ^ *** | 求幂            |
| ++ -- | 增加或减少，作为前缀或后缀 |

例：

```shell
awk 'BEGIN{a="b";print a++,++a;}'
0 2
```

注意：所有用作算术运算符进行操作，操作数自动转为数值，所有非数值都变为0
#### 赋值运算符

| 运算符                     | 描述   |
| ----------------------- | ---- |
| = += -= *= /= %= ^= **= | 赋值语句 |

例：

```shell
a+=5; 等价于：a=a+5; 其它同类
```

#### 逻辑运算符

|运算符|描述|
|---|---|
|`\|`|逻辑或|
|&&|逻辑与|

例：

```shell
awk 'BEGIN{a=1;b=2;print (a>5 && b<=2),(a>5 || b<=2);}'
0 1
```

#### 正则运算符

|运算符|描述|
|---|---|
|~ !~|匹配正则表达式和不匹配正则表达式|

```
^ 行首
$ 行尾
. 除了换行符以外的任意单个字符
* 前导字符的零个或多个
.* 所有字符
[] 字符组内的任一字符
[^]对字符组内的每个字符取反(不匹配字符组内的每个字符)
^[^] 非字符组内的字符开头的行
[a-z] 小写字母
[A-Z] 大写字母
[a-Z] 小写和大写字母
[0-9] 数字
\< 单词头单词一般以空格或特殊字符做分隔,连续的字符串被当做单词
\> 单词尾
```

> 正则需要用 /正则/ 包围住

例：

```shell
awk 'BEGIN{a="100testa";if(a ~ /^100*/){print "ok";}}'
ok
```

#### 关系运算符

|运算符|描述|
|---|---|
|< <= > >= != ==|关系运算符|

例：

```shell
awk 'BEGIN{a=11;if(a >= 9){print "ok";}}'
ok
```

注意：> < 可以作为字符串比较，也可以用作数值比较，关键看操作数如果是字符串就会转换为字符串比较。两个都为数字才转为数值比较。字符串比较：按照ASCII码顺序比较。

#### 其它运算符

|运算符|描述|
|---|---|
|$|字段引用|
|空格|字符串连接符|
|?:|C条件表达式|
|in|数组中是否存在某键值|

例：

```shell
awk 'BEGIN{a="b";print a=="b"?"ok":"err";}'
ok
```

```shell
awk 'BEGIN{a="b";arr[0]="b";arr[1]="c";print (a in arr);}'
0
```

```
awk 'BEGIN{a="b";arr[0]="b";arr["b"]="c";print (a in arr);}'
1
```

#### 运算级优先级表

!级别越高越优先  
级别越高越优先

#### awk高级输入输出

##### 读取下一条记录

awk中`next`语句使用：在循环逐行匹配，如果遇到next，就会跳过当前行，直接忽略下面语句。而进行下一行匹配。next语句一般用于多行合并：

```shell
cat text.txt
a
b
c
d
e

awk 'NR%2==1{next}{print NR,$0;}' text.txt
2 b
4 d
```

当记录行号除以2余1，就跳过当前行。下面的`print NR,$0`也不会执行。下一行开始，程序有开始判断`NR%2`值。这个时候记录行号是`：2` ，就会执行下面语句块：`'print NR,$0'`

跳过以“web”为首的行，再将该行内容分别与下面不以“web”为首的行合并打印，使用一个“：”和一个制表符连接：

```shell
cat text.txt
web01[192.168.2.100]
httpd            ok
tomcat               ok
sendmail               ok
web02[192.168.2.101]
httpd            ok
postfix               ok
web03[192.168.2.102]
mysqld            ok
httpd               ok
0
awk '/^web/{T=$0;next;}{print T":\t"$0;}' text.txt
web01[192.168.2.100]:   httpd            ok
web01[192.168.2.100]:   tomcat               ok
web01[192.168.2.100]:   sendmail               ok
web02[192.168.2.101]:   httpd            ok
web02[192.168.2.101]:   postfix               ok
web03[192.168.2.102]:   mysqld            ok
web03[192.168.2.102]:   httpd               ok
```

#### 简单地读取一条记录

`awk getline`用法：输出重定向需用到`getline函数`。getline从标准输入、管道或者当前正在处理的文件之外的其他输入文件获得输入。它负责从输入获得下一行的内容，并给NF,NR和FNR等内建变量赋值。如果得到一条记录，getline函数返回1，如果到达文件的末尾就返回0，如果出现错误，例如打开文件失败，就返回-1。

getline语法：getline var，变量var包含了特定行的内容。

awk getline从整体上来说，用法说明：

- **当其左右无重定向符`|`或`<`时：** getline作用于当前文件，读入当前文件的第一行给其后跟的变量`var`或`$0`（无变量），应该注意到，由于awk在处理getline之前已经读入了一行，所以getline得到的返回结果是隔行的。
- **当其左右有重定向符`|`或`<`时：** getline则作用于定向输入文件，由于该文件是刚打开，并没有被awk读入一行，只是getline读入，那么getline返回的是该文件的第一行，而不是隔行。

**示例：**

执行linux的`date`命令，并通过管道输出给`getline`，然后再把输出赋值给自定义变量out，并打印它：

```shell
awk 'BEGIN{ "date" | getline out; print out }' test
```

执行shell的date命令，并通过管道输出给getline，然后getline从管道中读取并将输入赋值给out，split函数把变量out转化成数组mon，然后打印数组mon的第二个元素：

```shell
awk 'BEGIN{ "date" | getline out; split(out,mon); print mon[2] }' test
```

命令ls的输出传递给geline作为输入，循环使getline从ls的输出中读取一行，并把它打印到屏幕。这里没有输入文件，因为BEGIN块在打开输入文件前执行，所以可以忽略输入文件。

```shell
awk 'BEGIN{ while( "ls" | getline) print }'
```

#### 关闭文件

awk中允许在程序中关闭一个输入或输出文件，方法是使用awk的close语句。

```shell
close("filename")
```

filename可以是getline打开的文件，也可以是stdin，包含文件名的变量或者getline使用的确切命令。或一个输出文件，可以是stdout，包含文件名的变量或使用管道的确切命令。

#### 输出到一个文件

awk中允许用如下方式将结果输出到一个文件：

```shell
echo | awk '{printf("hello word!n") > "datafile"}'
# 或
echo | awk '{printf("hello word!n") >> "datafile"}'
```

#### 设置字段定界符

默认的字段定界符是空格，可以使用`-F "定界符"` 明确指定一个定界符：

```shell
awk -F: '{ print $NF }' /etc/passwd
# 或
awk 'BEGIN{ FS=":" } { print $NF }' /etc/passwd
```

在`BEGIN语句块`中则可以用`OFS=“定界符”`设置输出字段的定界符。

#### 流程控制语句

在linux awk的while、do-while和for语句中允许使用break,continue语句来控制流程走向，也允许使用exit这样的语句来退出。break中断当前正在执行的循环并跳到循环外执行下一条语句。if 是流程选择用法。awk中，流程控制语句，语法结构，与c语言类型。有了这些语句，其实很多shell程序都可以交给awk，而且性能是非常快的。下面是各个语句用法。

#### 条件判断语句

```shell
if(表达式)
  语句1
else
  语句2
```

格式中语句1可以是多个语句，为了方便判断和阅读，最好将多个语句用{}括起来。awk分枝结构允许嵌套，其格式为：

```shell
if(表达式)
  {语句1}
else if(表达式)
  {语句2}
else
  {语句3}
```

示例：

```shell
awk 'BEGIN{
test=100;
if(test>90){
  print "very good";
  }
  else if(test>60){
    print "good";
  }
  else{
    print "no pass";
  }
}'

very good
```

每条命令语句后面可以用`;` **分号** 结尾。

#### 循环语句

##### while语句

```shell
while(表达式)
  {语句}
```

示例：

```shell
awk 'BEGIN{
test=100;
total=0;
while(i<=test){
  total+=i;
  i++;
}
print total;
}'
5050
```
##### for循环
for循环有两种格式：

格式1：

```shell
for(变量 in 数组)
  {语句}
```

示例：

```shell
awk 'BEGIN{
for(k in ENVIRON){
  print k"="ENVIRON[k];
}

}'
TERM=linux
G_BROKEN_FILENAMES=1
SHLVL=1
pwd=/root/text
...
logname=root
HOME=/root
SSH_CLIENT=192.168.1.21 53087 22
```

注：ENVIRON是awk常量，是子典型数组。

格式2：

```shell
for(变量;条件;表达式)
  {语句}
```

示例：

```shell
awk 'BEGIN{
total=0;
for(i=0;i<=100;i++){
  total+=i;
}
print total;
}'
5050
```

##### do循环

```shell
do
{语句} while(条件)
```

例子：

```shell
awk 'BEGIN{ 
total=0;
i=0;
do {total+=i;i++;} while(i<=100)
  print total;
}'
5050
```

##### 其他语句

- **break** 当 break 语句用于 while 或 for 语句时，导致退出程序循环。
- **continue** 当 continue 语句用于 while 或 for 语句时，使程序循环移动到下一个迭代。
- **next** 能能够导致读入下一个输入行，并返回到脚本的顶部。这可以避免对当前输入行执行其他的操作过程。
- **exit** 语句使主输入循环退出并将控制转移到END,如果END存在的话。如果没有定义END规则，或在END中应用exit语句，则终止脚本的执行。

#### 数组应用

数组是awk的灵魂，处理文本中最不能少的就是它的数组处理。因为数组索引（下标）可以是数字和字符串在awk中数组叫做关联数组(associative arrays)。awk 中的数组不必提前声明，也不必声明大小。数组元素用0或空字符串来初始化，这根据上下文而定。

#### 数组的定义

数字做数组索引（下标）：

```shell
Array[1]="sun"
Array[2]="kai"
```

字符串做数组索引（下标）：

```shell
Array["first"]="www"
Array["last"]="name"
Array["birth"]="1987"
```

使用中`print Array[1]`会打印出sun；使用`print Array[2]`会打印出kai；使用`print["birth"]`会得到1987。

**读取数组的值**

```shell
{ for(item in array) {print array[item]}; }       #输出的顺序是随机的
{ for(i=1;i<=len;i++) {print array[i]}; }         #Len是数组的长度
```

#### 数组相关函数

**得到数组长度：**

```shell
awk 'BEGIN{info="it is a test";lens=split(info,tA," ");print length(tA),lens;}'
4 4
```

length返回字符串以及数组长度，split进行分割字符串为数组，也会返回分割得到数组长度。

```shell
awk 'BEGIN{info="it is a test";split(info,tA," ");print asort(tA);}'
4
```

asort对数组进行排序，返回数组长度。

**输出数组内容（无序，有序输出）：**

```shell
awk 'BEGIN{info="it is a test";split(info,tA," ");for(k in tA){print k,tA[k];}}'
4 test
1 it
2 is
3 a 
```

`for…in`输出，因为数组是关联数组，默认是无序的。所以通过`for…in`得到是无序的数组。如果需要得到有序数组，需要通过下标获得。

```shell
awk 'BEGIN{info="it is a test";tlen=split(info,tA," ");for(k=1;k<=tlen;k++){print k,tA[k];}}'
1 it
2 is
3 a
4 test
```

注意：数组下标是从1开始，与C数组不一样。

**判断键值存在以及删除键值：**

```shell
# 错误的判断方法：
awk 'BEGIN{tB["a"]="a1";tB["b"]="b1";if(tB["c"]!="1"){print "no found";};for(k in tB){print k,tB[k];}}' 
no found
a a1
b b1
c
```

以上出现奇怪问题，`tB[“c”]`没有定义，但是循环时候，发现已经存在该键值，它的值为空，这里需要注意，awk数组是关联数组，只要通过数组引用它的key，就会自动创建改序列。

```shell
# 正确判断方法：
awk 'BEGIN{tB["a"]="a1";tB["b"]="b1";if( "c" in tB){print "ok";};for(k in tB){print k,tB[k];}}'  
a a1
b b1
```

`if(key in array)`通过这种方法判断数组中是否包含`key`键值。

```shell
#删除键值：
awk 'BEGIN{tB["a"]="a1";tB["b"]="b1";delete tB["a"];for(k in tB){print k,tB[k];}}'                     
b b1
```

`delete array[key]`可以删除，对应数组`key`的，序列值。

#### 二维、多维数组使用

awk的多维数组在本质上是一维数组，更确切一点，awk在存储上并不支持多维数组。awk提供了逻辑上模拟二维数组的访问方式。例如，`array[2,4]=1`这样的访问是允许的。awk使用一个特殊的字符串`SUBSEP(\034)`作为分割字段，在上面的例子中，关联数组array存储的键值实际上是2\0344。

类似一维数组的成员测试，多维数组可以使用`if ( (i,j) in array)`这样的语法，但是下标必须放置在圆括号中。类似一维数组的循环访问，多维数组使用`for ( item in array )`这样的语法遍历数组。与一维数组不同的是，多维数组必须使用`split()`函数来访问单独的下标分量。

```shell
awk 'BEGIN{
for(i=1;i<=9;i++){
  for(j=1;j<=9;j++){
    tarr[i,j]=i*j; print i,"*",j,"=",tarr[i,j];
  }
}
}'
1 * 1 = 1
1 * 2 = 2
1 * 3 = 3
1 * 4 = 4
1 * 5 = 5
1 * 6 = 6 
...
9 * 6 = 54
9 * 7 = 63
9 * 8 = 72
9 * 9 = 81
```

可以通过`array[k,k2]`引用获得数组内容。

另一种方法：

```shell
awk 'BEGIN{
for(i=1;i<=9;i++){
  for(j=1;j<=9;j++){
    tarr[i,j]=i*j;
  }
}
for(m in tarr){
  split(m,tarr2,SUBSEP); print tarr2[1],"*",tarr2[2],"=",tarr[m];
}
}'
```

#### 内置函数

awk内置函数，主要分以下3种类似：算数函数、字符串函数、其它一般函数、时间函数。

#### 算术函数

| 格式              | 描述                                                         |
| --------------- | ---------------------------------------------------------- |
| atan2( y, x )   | 返回 y/x 的反正切。                                               |
| cos( x )        | 返回 x 的余弦；x 是弧度。                                            |
| sin( x )        | 返回 x 的正弦；x 是弧度。                                            |
| exp( x )        | 返回 x 幂函数。                                                  |
| log( x )        | 返回 x 的自然对数。                                                |
| sqrt( x )       | 返回 x 平方根。                                                  |
| int( x )        | 返回 x 的截断至整数的值。                                             |
| rand( )         | 返回任意数字 n，其中 0 <= n < 1。                                    |
| srand( [expr] ) | 将 rand 函数的种子值设置为 Expr 参数的值，或如果省略 Expr 参数则使用某天的时间。返回先前的种子值。 |

举例说明：

```shell
awk 'BEGIN{OFMT="%.3f";fs=sin(1);fe=exp(10);fl=log(10);fi=int(3.1415);print fs,fe,fl,fi;}'
0.841 22026.466 2.303 3

```

OFMT 设置输出数据格式是保留3位小数。

获得随机数：

```shell
awk 'BEGIN{srand();fr=int(100*rand());print fr;}'
78
awk 'BEGIN{srand();fr=int(100*rand());print fr;}'
31
awk 'BEGIN{srand();fr=int(100*rand());print fr;}'
41 
```

#### 字符串函数

|格式|描述|
|---|---|
|gsub( Ere, Repl, [ In ] )|除了正则表达式所有具体值被替代这点，它和 sub 函数完全一样地执行。|
|sub( Ere, Repl, [ In ] )|用 Repl 参数指定的字符串替换 In 参数指定的字符串中的由 Ere 参数指定的扩展正则表达式的第一个具体值。sub 函数返回替换的数量。出现在 Repl 参数指定的字符串中的 &（和符号）由 In 参数指定的与 Ere 参数的指定的扩展正则表达式匹配的字符串替换。如果未指定 In 参数，缺省值是整个记录（$0 记录变量）。|
|index( String1, String2 )|在由 String1 参数指定的字符串（其中有出现 String2 指定的参数）中，返回位置，从 1 开始编号。如果 String2 参数不在 String1 参数中出现，则返回 0（零）。|
|length [(String)]|返回 String 参数指定的字符串的长度（字符形式）。如果未给出 String 参数，则返回整个记录的长度（$0 记录变量）。|
|blength [(String)]|返回 String 参数指定的字符串的长度（以字节为单位）。如果未给出 String 参数，则返回整个记录的长度（$0 记录变量）。|
|substr( String, M, [ N ] )|返回具有 N 参数指定的字符数量子串。子串从 String 参数指定的字符串取得，其字符以 M 参数指定的位置开始。M 参数指定为将 String 参数中的第一个字符作为编号 1。如果未指定 N 参数，则子串的长度将是 M 参数指定的位置到 String 参数的末尾 的长度。|
|match( String, Ere )|在 String 参数指定的字符串（Ere 参数指定的扩展正则表达式出现在其中）中返回位置（字符形式），从 1 开始编号，或如果 Ere 参数不出现，则返回 0（零）。RSTART 特殊变量设置为返回值。RLENGTH 特殊变量设置为匹配的字符串的长度，或如果未找到任何匹配，则设置为 -1（负一）。|
|split( String, A, [Ere] )|将 String 参数指定的参数分割为数组元素 A[1], A[2], . . ., A[n]，并返回 n 变量的值。此分隔可以通过 Ere 参数指定的扩展正则表达式进行，或用当前字段分隔符（FS 特殊变量）来进行（如果没有给出 Ere 参数）。除非上下文指明特定的元素还应具有一个数字值，否则 A 数组中的元素用字符串值来创建。|
|tolower( String )|返回 String 参数指定的字符串，字符串中每个大写字符将更改为小写。大写和小写的映射由当前语言环境的 LC_CTYPE 范畴定义。|
|toupper( String )|返回 String 参数指定的字符串，字符串中每个小写字符将更改为大写。大写和小写的映射由当前语言环境的 LC_CTYPE 范畴定义。|
|sprintf(Format, Expr, Expr, . . . )|根据 Format 参数指定的 printf 子例程格式字符串来格式化 Expr 参数指定的表达式并返回最后生成的字符串。|

注：Ere都可以是正则表达式。

**gsub,sub使用**

```shell
awk 'BEGIN{info="this is a test2010test!";gsub(/[0-9]+/,"!",info);print info}'
this is a test!test!
```

在 info中查找满足正则表达式，`/[0-9]+/` 用`””`替换，并且替换后的值，赋值给info 未给info值，默认是`$0`

**查找字符串（index使用）**

```shell
awk 'BEGIN{info="this is a test2010test!";print index(info,"test")?"ok":"no found";}'
ok
```

未找到，返回0

**正则表达式匹配查找(match使用）**

```
awk 'BEGIN{info="this is a test2010test!";print match(info,/[0-9]+/)?"ok":"no found";}'
ok
```

**截取字符串(substr使用）**

```shell
[wangsl@centos5 ~]$ awk 'BEGIN{info="this is a test2010test!";print substr(info,4,10);}'
s is a tes
```

从第 4个 字符开始，截取10个长度字符串

**字符串分割（split使用）**

```shell
awk 'BEGIN{info="this is a test";split(info,tA," ");print length(tA);for(k in tA){print k,tA[k];}}'
4
4 test
1 this
2 is
3 a
```

分割info，动态创建数组tA，这里比较有意思，`awk for …in`循环，是一个无序的循环。 并不是从数组下标1…n ，因此使用时候需要注意。

**格式化字符串输出（sprintf使用）**

格式化字符串格式：

其中格式化字符串包括两部分内容：一部分是正常字符，这些字符将按原样输出; 另一部分是格式化规定字符，以`"%"`开始，后跟一个或几个规定字符,用来确定输出内容格式。

|格式|描述|格式|描述|
|---|---|---|---|
|%d|十进制有符号整数|%u|十进制无符号整数|
|%f|浮点数|%s|字符串|
|%c|单个字符|%p|指针的值|
|%e|指数形式的浮点数|%x|%X 无符号以十六进制表示的整数|
|%o|无符号以八进制表示的整数|%g|自动选择合适的表示法|

```shell
awk 'BEGIN{n1=124.113;n2=-1.224;n3=1.2345; printf("%.2f,%.2u,%.2g,%X,%on",n1,n2,n3,n1,n1);}'
124.11,18446744073709551615,1.2,7C,174
```

#### 一般函数

| 格式                                   | 描述                                                                                                                                                                                                                                                                                               |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| close( Expression )                  | 用同一个带字符串值的 Expression 参数来关闭由 print 或 printf 语句打开的或调用 getline 函数打开的文件或管道。如果文件或管道成功关闭，则返回 0；其它情况下返回非零值。如果打算写一个文件，并稍后在同一个程序中读取文件，则 close 语句是必需的。                                                                                                                                                    |
| system(command )                     | 执行 Command 参数指定的命令，并返回退出状态。等同于 system 子例程。                                                                                                                                                                                                                                                       |
| Expression `\|` getline [ Variable ] | 从来自 Expression 参数指定的命令的输出中通过管道传送的流中读取一个输入记录，并将该记录的值指定给 Variable 参数指定的变量。如果当前未打开将 Expression 参数的值作为其命令名称的流，则创建流。创建的流等同于调用 popen 子例程，此时 Command 参数取 Expression 参数的值且 Mode 参数设置为一个是 r 的值。只要流保留打开且 Expression 参数求得同一个字符串，则对 getline 函数的每次后续调用读取另一个记录。如果未指定 Variable 参数，则 $0 记录变量和 NF 特殊变量设置为从流读取的记录。 |
| getline [ Variable ] < Expression    | 从 Expression 参数指定的文件读取输入的下一个记录，并将 Variable 参数指定的变量设置为该记录的值。只要流保留打开且 Expression 参数对同一个字符串求值，则对 getline 函数的每次后续调用读取另一个记录。如果未指定 Variable 参数，则 $0 记录变量和 NF 特殊变量设置为从流读取的记录。                                                                                                                           |
| getline [ Variable ]                 | 将 Variable 参数指定的变量设置为从当前输入文件读取的下一个输入记录。如果未指定 Variable 参数，则 $0 记录变量设置为该记录的值，还将设置 NF、NR 和 FNR 特殊变量。                                                                                                                                                                                                |

**打开外部文件（close用法）**

```shell
awk 'BEGIN{while("cat /etc/passwd"|getline){print $0;};close("/etc/passwd");}'
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
```

**逐行读取外部文件(getline使用方法）**

```shell
awk 'BEGIN{while(getline < "/etc/passwd"){print $0;};close("/etc/passwd");}'
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
```

```shell
awk 'BEGIN{print "Enter your name:";getline name;print name;}'
Enter your name:
chengmo
chengmo
```

**调用外部应用程序(system使用方法）**

```shell
awk 'BEGIN{b=system("ls -al");print b;}'
total 42092
drwxr-xr-x 14 chengmo chengmo     4096 09-30 17:47 .
drwxr-xr-x 95 root   root       4096 10-08 14:01 ..
```

b返回值，是执行结果。

#### 时间函数

| 格式                                 | 描述                                  |
| ---------------------------------- | ----------------------------------- |
| 函数名                                | 说明                                  |
| mktime( YYYY MM dd HH MM ss[ DST]) | 生成时间格式                              |
| strftime([format [, timestamp]])   | 格式化时间输出，将时间戳转为时间字符串具体格式，见下表。        |
| systime()                          | 得到时间戳，返回从1970年1月1日开始到当前时间(不计闰年)的整秒数 |

**建指定时间(mktime使用）**

```shell
awk 'BEGIN{tstamp=mktime("2001 01 01 12 12 12");print strftime("%c",tstamp);}'
2001年01月01日 星期一 12时12分12秒
```

```shell
awk 'BEGIN{tstamp1=mktime("2001 01 01 12 12 12");tstamp2=mktime("2001 02 01 0 0 0");print tstamp2-tstamp1;}'
2634468
```

求2个时间段中间时间差，介绍了strftime使用方法

```shell
awk 'BEGIN{tstamp1=mktime("2001 01 01 12 12 12");tstamp2=systime();print tstamp2-tstamp1;}' 
308201392
```

**strftime日期和时间格式说明符**

|格式|描述|
|---|---|
|%a|星期几的缩写(Sun)|
|%A|星期几的完整写法(Sunday)|
|%b|月名的缩写(Oct)|
|%B|月名的完整写法(October)|
|%c|本地日期和时间|
|%d|十进制日期|
|%D|日期 08/20/99|
|%e|日期，如果只有一位会补上一个空格|
|%H|用十进制表示24小时格式的小时|
|%I|用十进制表示12小时格式的小时|
|%j|从1月1日起一年中的第几天|
|%m|十进制表示的月份|
|%M|十进制表示的分钟|
|%p|12小时表示法(AM/PM)|
|%S|十进制表示的秒|
|%U|十进制表示的一年中的第几个星期(星期天作为一个星期的开始)|
|%w|十进制表示的星期几(星期天是0)|
|%W|十进制表示的一年中的第几个星期(星期一作为一个星期的开始)|
|%x|重新设置本地日期(08/20/99)|
|%X|重新设置本地时间(12:00:00)|
|%y|两位数字表示的年(99)|
|%Y|当前月份|
|%%|百分号(%)|
### 12. sed

功能强大的流式文本编辑器
#### 补充说明

**sed** 是一种流编辑器，它是文本处理中非常重要的工具，能够完美的配合正则表达式使用，功能不同凡响。处理时，把当前处理的行存储在临时缓冲区中，称为“模式空间”（pattern space），接着用sed命令处理缓冲区中的内容，处理完成后，把缓冲区的内容送往屏幕。接着处理下一行，这样不断重复，直到文件末尾。文件内容并没有 改变，除非你使用重定向存储输出。Sed主要用来自动编辑一个或多个文件；简化对文件的反复操作；编写转换程序等。

#### sed的选项、命令、替换标记

**命令格式**

```shell
sed [options] 'command' file(s)
sed [options] -f scriptfile file(s)
```

#### 选项

```shell
-e<script>或--expression=<script>：以选项中的指定的script来处理输入的文本文件；
-f<script文件>或--file=<script文件>：以选项中指定的script文件来处理输入的文本文件；
-h或--help：显示帮助；
-n或--quiet或——silent：仅显示script处理后的结果；
-V或--version：显示版本信息。
```

#### 参数

文件：指定待处理的文本文件列表。

#### sed命令

```shell
a\ # 在当前行下面插入文本。
i\ # 在当前行上面插入文本。
c\ # 把选定的行改为新的文本。
d # 删除，删除选择的行。
D # 删除模板块的第一行。
s # 替换指定字符
h # 拷贝模板块的内容到内存中的缓冲区。
H # 追加模板块的内容到内存中的缓冲区。
g # 获得内存缓冲区的内容，并替代当前模板块中的文本。
G # 获得内存缓冲区的内容，并追加到当前模板块文本的后面。
l # 列表不能打印字符的清单。
n # 读取下一个输入行，用下一个命令处理新的行而不是用第一个命令。
N # 追加下一个输入行到模板块后面并在二者间嵌入一个新行，改变当前行号码。
p # 打印模板块的行。
P # (大写) 打印模板块的第一行。
q # 退出Sed。
b lable # 分支到脚本中带有标记的地方，如果分支不存在则分支到脚本的末尾。
r file # 从file中读行。
t label # if分支，从最后一行开始，条件一旦满足或者T，t命令，将导致分支到带有标号的命令处，或者到脚本的末尾。
T label # 错误分支，从最后一行开始，一旦发生错误或者T，t命令，将导致分支到带有标号的命令处，或者到脚本的末尾。
w file # 写并追加模板块到file末尾。  
W file # 写并追加模板块的第一行到file末尾。  
! # 表示后面的命令对所有没有被选定的行发生作用。  
= # 打印当前行号码。  
# # 把注释扩展到下一个换行符以前。  
```

#### sed替换标记

```shell
g # 表示行内全面替换。  
p # 表示打印行。  
w # 表示把行写入一个文件。  
x # 表示互换模板块中的文本和缓冲区中的文本。  
y # 表示把一个字符翻译为另外的字符（但是不用于正则表达式）
\1 # 子串匹配标记
& # 已匹配字符串标记
```

#### sed元字符集

```shell
^ # 匹配行开始，如：/^sed/匹配所有以sed开头的行。
$ # 匹配行结束，如：/sed$/匹配所有以sed结尾的行。
. # 匹配一个非换行符的任意字符，如：/s.d/匹配s后接一个任意字符，最后是d。
* # 匹配0个或多个字符，如：/*sed/匹配所有模板是一个或多个空格后紧跟sed的行。
[] # 匹配一个指定范围内的字符，如/[sS]ed/匹配sed和Sed。  
[^] # 匹配一个不在指定范围内的字符，如：/[^A-RT-Z]ed/匹配不包含A-R和T-Z的一个字母开头，紧跟ed的行。
\(..\) # 匹配子串，保存匹配的字符，如s/\(love\)able/\1rs，loveable被替换成lovers。
& # 保存搜索字符用来替换其他字符，如s/love/ **&** /，love这成 **love** 。
\< # 匹配单词的开始，如:/\<love/匹配包含以love开头的单词的行。
\> # 匹配单词的结束，如/love\>/匹配包含以love结尾的单词的行。
x\{m\} # 重复字符x，m次，如：/0\{5\}/匹配包含5个0的行。
x\{m,\} # 重复字符x，至少m次，如：/0\{5,\}/匹配至少有5个0的行。
x\{m,n\} # 重复字符x，至少m次，不多于n次，如：/0\{5,10\}/匹配5~10个0的行。  
```

## [](https://wangchujiang.com/linux-command/c/sed.html#sed%E7%94%A8%E6%B3%95%E5%AE%9E%E4%BE%8B)sed用法实例

### [](https://wangchujiang.com/linux-command/c/sed.html#%E6%9B%BF%E6%8D%A2%E6%93%8D%E4%BD%9Cs%E5%91%BD%E4%BB%A4)替换操作：s命令

替换文本中的字符串：

```shell
sed 's/book/books/' file
```

**-n选项** 和 **p命令** 一起使用表示只打印那些发生替换的行：

sed -n 's/test/TEST/p' file

直接编辑文件 **选项-i** ，会匹配file文件中每一行的所有book替换为books：

```shell
sed -i 's/book/books/g' file
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%85%A8%E9%9D%A2%E6%9B%BF%E6%8D%A2%E6%A0%87%E8%AE%B0g)全面替换标记g

使用后缀 /g 标记会替换每一行中的所有匹配：

```shell
sed 's/book/books/g' file
```

当需要从第N处匹配开始替换时，可以使用 /Ng：

```shell
echo sksksksksksk | sed 's/sk/SK/2g'
skSKSKSKSKSK

echo sksksksksksk | sed 's/sk/SK/3g'
skskSKSKSKSK

echo sksksksksksk | sed 's/sk/SK/4g'
skskskSKSKSK
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%AE%9A%E7%95%8C%E7%AC%A6)定界符

以上命令中字符 / 在sed中作为定界符使用，也可以使用任意的定界符：

```shell
sed 's:test:TEXT:g'
sed 's|test|TEXT|g'
```

定界符出现在样式内部时，需要进行转义：

```shell
sed 's/\/bin/\/usr\/local\/bin/g'
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%88%A0%E9%99%A4%E6%93%8D%E4%BD%9Cd%E5%91%BD%E4%BB%A4)删除操作：d命令

删除空白行：

```shell
sed '/^$/d' file
```

删除文件的第2行：

```shell
sed '2d' file
```

删除文件的第2行到末尾所有行：

```shell
sed '2,$d' file
```

删除文件最后一行：

```shell
sed '$d' file
```

删除文件中所有开头是test的行(d写外边效果一样)：

```shell
sed '/^test/d' file
sed '/^test/'d file
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%B7%B2%E5%8C%B9%E9%85%8D%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%A0%87%E8%AE%B0)已匹配字符串标记&

正则表达式 \w+ 匹配每一个单词，使用 [&] 替换它，& 对应于之前所匹配到的单词：

```shell
echo this is a test line | sed 's/\w\+/[&]/g'
[this] [is] [a] [test] [line]
```

所有以192.168.0.1开头的行都会被替换成它自已加localhost：

```shell
sed 's/^192.168.0.1/&localhost/' file
192.168.0.1localhost
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%AD%90%E4%B8%B2%E5%8C%B9%E9%85%8D%E6%A0%87%E8%AE%B01)子串匹配标记\1

匹配给定样式的其中一部分：

```shell
echo this is digit 7 in a number | sed 's/digit \([0-9]\)/\1/'
this is 7 in a number
```

命令中 digit 7，被替换成了 7。样式匹配到的子串是 7，(..) 用于匹配子串，对于匹配到的第一个子串就标记为 **\1** ，依此类推匹配到的第二个结果就是 **\2** ，例如：

```shell
echo aaa BBB | sed 's/\([a-z]\+\) \([A-Z]\+\)/\2 \1/'
BBB aaa
```

love被标记为1，所有loveable会被替换成lovers，并打印出来：

```shell
sed -n 's/\(love\)able/\1rs/p' file
```

通过替换获取ip：

```shell
ifconfig ens32 | sed -n '/inet /p' | sed 's/inet \([0-9.]\+\).*/\1/'
192.168.75.126
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%A4%A7%E5%B0%8F%E5%86%99%E8%BD%AC%E6%8D%A2ul)大小写转换U/L

```shell
\u：	首字母转换为大写
\U：  全部转换为大写
\l：	 首字母转换为小写
\L：	 全部转换为小写
```

首字母转换为大写：

```shell
[root@node6 ~]# sed 's/^[a-z]\+/\u&/' passwd 
Root:x:0:0:root:/root:/bin/bash
Bin:x:1:1:bin:/bin:/sbin/nologin
Daemon:x:2:2:daemon:/sbin:/sbin/nologin
Adm:x:3:4:adm:/var/adm:/sbin/nologin
Lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
Sync:x:5:0:sync:/sbin:/bin/sync
```

匹配到的字符全部转换为大写：

```shell
[root@node6 ~]# sed 's/^[a-z]\+/\U&/' passwd 
ROOT:x:0:0:root:/root:/bin/bash
BIN:x:1:1:bin:/bin:/sbin/nologin
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E7%BB%84%E5%90%88%E5%A4%9A%E4%B8%AA%E8%A1%A8%E8%BE%BE%E5%BC%8F)组合多个表达式

1. 替换文本中的多个字符串：

```shell
sed -e 's/old_string/new_string/g' -e 's/another_old_string/another_new_string/g' file.txt
```

2. 删除文本中的多个行：

```shell
sed -e '1d' -e '/pattern/d' file.txt
```

3. 在文本中插入多个行：

```shell
sed -e '1i\inserted_line1' -e '2i\inserted_line2' file.txt
```

其中，-e 表示指定一个表达式，多个表达式之间用 -e 分隔。每个表达式可以是一个 sed 命令，例如 s、d、i 等。

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%BC%95%E7%94%A8)引用

sed表达式可以使用单引号来引用，但是如果表达式内部包含变量字符串，就需要使用双引号。

```shell
test=hello
echo hello WORLD | sed "s/$test/HELLO"
HELLO WORLD
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E9%80%89%E5%AE%9A%E8%A1%8C%E7%9A%84%E8%8C%83%E5%9B%B4%E9%80%97%E5%8F%B7)选定行的范围：,（逗号）

所有在模板test和check所确定的范围内的行都被打印：

```shell
sed -n '/test/,/check/p' file
```

打印从第5行开始到第一个包含以test开始的行之间的所有行：

```shell
sed -n '5,/^test/p' file
```

对于模板test和west之间的行，每行的末尾用字符串aaa bbb替换：

```shell
sed '/test/,/west/s/$/aaa bbb/' file
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%A4%9A%E7%82%B9%E7%BC%96%E8%BE%91e%E5%91%BD%E4%BB%A4)多点编辑：e命令

-e选项允许在同一行里执行多条命令：

```shell
sed -e '1,5d' -e 's/test/check/' file
```

上面sed表达式的第一条命令删除1至5行，第二条命令用check替换test。命令的执行顺序对结果有影响。如果两个命令都是替换命令，那么第一个替换命令将影响第二个替换命令的结果。

和 -e 等价的命令是 --expression：

```shell
sed --expression='s/test/check/' --expression='/love/d' file
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E4%BB%8E%E6%96%87%E4%BB%B6%E8%AF%BB%E5%85%A5r%E5%91%BD%E4%BB%A4)从文件读入：r命令

file里的内容被读进来，显示在与test匹配的行后面，如果匹配多行，则file的内容将显示在所有匹配行的下面：

```shell
sed '/test/r file' filename
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%86%99%E5%85%A5%E6%96%87%E4%BB%B6w%E5%91%BD%E4%BB%A4-)写入文件：w命令  

在example中所有包含test的行都被写入file里：

```shell
sed -n '/test/w file' example
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E8%BF%BD%E5%8A%A0%E8%A1%8C%E4%B8%8Ba%E5%91%BD%E4%BB%A4)追加（行下）：a\命令

将 this is a test line 追加到 以test 开头的行后面：

```shell
sed '/^test/a\this is a test line' file
```

在 test.conf 文件第2行之后插入 this is a test line：

```shell
sed -i '2a\this is a test line' test.conf
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E6%8F%92%E5%85%A5%E8%A1%8C%E4%B8%8Ai%E5%91%BD%E4%BB%A4)插入（行上）：i\命令

将 this is a test line 追加到以test开头的行前面：

```shell
sed '/^test/i\this is a test line' file
```

在test.conf文件第5行之前插入this is a test line：

```shell
sed -i '5i\this is a test line' test.conf
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E6%9B%BF%E6%8D%A2%E6%8C%87%E5%AE%9A%E8%A1%8Cc%E5%91%BD%E4%BB%A4)替换指定行：c\命令

把root开头的行替换新内容：

```shell
[root@node6 ~]# sed '/^root/c this is new line!' passwd 
this is new line!
bin:x:1:1:bin:/bin:/sbin/nologin
```

如果是指定范围替换，需要注意，sed不是每行进行替换，而是把整个范围作为整体替换：

```shell
[root@node6 ~]# nl passwd | sed '1,5c\   this is dangerous!'
     this is dangerous!
     6	sync:x:5:0:sync:/sbin:/bin/sync
     7	shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
```

如果想实现对第一行到第五行统一替换为相同内容，可以用下面的命令实现：

```shell
[root@node5 ~]# sed '1{:a;s/.*/lutxixia/;n;6!ba}' passwd 
lutxixia
lutxixia
lutxixia
lutxixia
lutxixia
sync:x:5:0:sync:/sbin:/bin/sync

其中：
:a  	是设置一个循环标签
s/.*/lutixia/	是用lutixia字符替换匹配到的每行内容
n	是读取下一行
6!	是读到第六行退出循环，终止操作,如果没有，则继续循环。
ba	是如果没有到第六行就跳转到a继续循环
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E4%B8%8B%E4%B8%80%E4%B8%AAn%E5%91%BD%E4%BB%A4)下一个：n命令

如果test被匹配，则移动到匹配行的下一行，替换这一行的aa，变为bb，并打印该行，然后继续：

```shell
sed '/test/{ n; s/aa/bb/; }' file
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E5%8F%98%E5%BD%A2y%E5%91%BD%E4%BB%A4)变形：y命令

把1~10行内所有abcde转变为大写，注意，正则表达式元字符不能使用这个命令：

```shell
sed '1,10y/abcde/ABCDE/' file
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E9%80%80%E5%87%BAq%E5%91%BD%E4%BB%A4)退出：q命令

打印完前10行后，退出sed:

```shell
sed '10q' file
```

直到找到第一个匹配项，退出sed：

```shell
[root@node4 ~]# sed  '/nginx/q' nginx.yml 
---
- hosts: nginx
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E4%BF%9D%E6%8C%81%E5%92%8C%E8%8E%B7%E5%8F%96h%E5%91%BD%E4%BB%A4%E5%92%8Cg%E5%91%BD%E4%BB%A4)保持和获取：h命令和G命令

在sed处理文件的时候，每一行都被保存在一个叫模式空间的临时缓冲区中，除非行被删除或者输出被取消，否则所有被处理的行都将 打印在屏幕上。接着模式空间被清空，并存入新的一行等待处理。

```shell
sed -e '/test/h' -e '$G' file
```

在这个例子里，匹配test的行被找到后，将存入模式空间，h命令将其复制并存入一个称为保持缓存区的特殊缓冲区内。第二条语句的意思是，当到达最后一行后，G命令取出保持缓冲区的行，然后把它放回模式空间中，且追加到现在已经存在于模式空间中的行的末尾。在这个例子中就是追加到最后一行。简单来说，任何包含test的行都被复制并追加到该文件的末尾。

### [](https://wangchujiang.com/linux-command/c/sed.html#%E4%BF%9D%E6%8C%81%E5%92%8C%E4%BA%92%E6%8D%A2h%E5%91%BD%E4%BB%A4%E5%92%8Cx%E5%91%BD%E4%BB%A4)保持和互换：h命令和x命令

互换模式空间和保持缓冲区的内容。也就是把包含test与check的行互换：

```shell
sed -e '/test/h' -e '/check/x' file
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E8%84%9A%E6%9C%ACscriptfile)脚本scriptfile

sed脚本是一个sed的命令清单，启动Sed时以-f选项引导脚本文件名。Sed对于脚本中输入的命令非常挑剔，在命令的末尾不能有任何空白或文本，如果在一行中有多个命令，要用分号分隔。以#开头的行为注释行，且不能跨行。

```shell
sed [options] -f scriptfile file(s)
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E6%89%93%E5%8D%B0%E5%A5%87%E6%95%B0%E8%A1%8C%E6%88%96%E5%81%B6%E6%95%B0%E8%A1%8C)打印奇数行或偶数行

方法1：

```shell
sed -n 'p;n' test.txt  #奇数行
sed -n 'n;p' test.txt  #偶数行
```

方法2：

```shell
sed -n '1~2p' test.txt  #奇数行
sed -n '2~2p' test.txt  #偶数行
```

### [](https://wangchujiang.com/linux-command/c/sed.html#%E6%89%93%E5%8D%B0%E5%8C%B9%E9%85%8D%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84%E4%B8%8B%E4%B8%80%E8%A1%8C)打印匹配字符串的下一行

```shell
grep -A 1 SCC URFILE
sed -n '/SCC/{n;p}' URFILE
awk '/SCC/{getline; print}' URFILE
```
