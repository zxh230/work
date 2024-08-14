从RHEL升级到9版本之后内核版本升级为5.14，namespace和cgroup也随之进行了更新。

cgroup的修改主要集中在设置方法上，在5版本内核以前，采用的伪文件系统直接修改，加上设置task的PID方法。但是此方法最大的问题是目录结构复杂，结构冗余等问题。

在新版内核的修改中，主要修改了伪文件系统的目录位置，结构调整等。当然具体的参数也被大幅削减，保留了每个程序的必备参数，其他无关参数被默认取消。

整个设置逻辑变为：在proc的pid进程内的cgroup文件声明伪文件系统的目录位置。所有的进程独立创建一个cgroup目录存放参数。

确认当前的内核版本：

```bash
[root@server1 ~]# uname -aLinux server1 5.14.0-162.6.1.el9_1.0.1.x86_64 #1 SMP PREEMPT_DYNAMIC Mon Nov 28 18:44:09 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux[root@server1 ~]# cat /etc/redhat-release Rocky Linux release 9.1 (Blue Onyx)
```

### 术语

“cgroup”代表“control group”，从不大写。单数形式用于指定整个特征，也用作“cgroup controllers”中的限定符。当明确提及多个单独的对照组时，使用复数形式“cgroups”。

什么是cgroups?

cgroup是一种分层组织过程并以可控和可配置的方式沿分层分布系统资源的机制。

cgroup主要由核心和控制器两部分组成。

- cgroup核心主要负责分层组织流程。

- cgroup控制器通常负责沿着层次结构分配特定类型的系统资源，尽管存在用于资源分配以外的目的的实用程序控制器。


有五个特点

1. cgroups形成一个树结构，系统中的每个进程都属于一个并且只能属于一个cgroup。

2. 进程的下的所有线程都属于同一个cgroup。

3. 创建时，所有进程都被放入父进程当时所属的cgroup中。

4. 一个进程可以迁移到另一个cgroup。

5. 进程的迁移不会影响现有的子进程。


根据某些结构约束，可以在cgroup上选择性地启用或禁用控制器。所有控制器行为都是分层的-如果在一个cgroup上启用了一个控制器，它会影响属于由cgroup的包含子层次结构组成的cgroups的所有进程。当在一个嵌套的控制组上启用一个控制器时，它总是会进一步限制资源分配。在层次结构中更靠近根部设置的限制无法被更远处的设置所覆盖。简单解释就是下层级的设置不会覆盖上层级的设置。

这里需要注意的是：与v1不同，cgroup v2只有一个层次结构。cgroup v2层次结构可以使用以下mount命令进行挂载。

语法如下：

```bash
# mount -t cgroup2 none $MOUNT_POINT
```

所有支持v2且未绑定到v1层次结构的控制器都会自动绑定到v2层次结构并显示在根目录中。在v2层次结构中未处于活动使用中的控制器可以绑定到其他层次结构。这允许以完全向后兼容的方式将v2层次结构与传统的v1多层次结构混合。

只有在控制器在其当前层次结构中不再被引用后，才能在层次结构之间移动控制器。由于每个cgroup的控制器状态是异步销毁的，并且控制器可能具有延迟引用，因此在上一层次结构的最终umount之后，控制器可能不会立即出现在v2层次结构上。类似地，控制器应该被完全禁用以移出统一层次结构，并且禁用的控制器可能需要一些时间才能用于其他层次结构；此外，由于控制器之间的依赖性，其他控制器可能也需要被禁用。

虽然对开发和手动配置很有用，但强烈反对在v2和其他层次结构之间动态移动控制器以供生产使用。建议在系统引导后开始使用控制器之前，先确定层次结构和控制器关联。

在转换到v2的过程中，系统管理软件可能仍然会自动安装v1-cgroup文件系统，因此在手动干预之前，会在引导期间劫持所有控制器。为了使测试和实验更容易，内核参数cgroup_no_v1=允许在v1中禁用控制器，并使它们在v2中始终可用。

cgroup v2当前支持以下装载选项。(这几个选项可以在下面"Cgroup挂载点"的部分看到.)

nsdelegate

将cgroup命名空间视为委派边界。此选项是系统范围的，只能在装载时设置，也只能通过从init命名空间重新装载进行修改。在非init命名空间装载上会忽略mount选项。有关详细信息，请参阅“委派”部分。

favordynmods

减少动态cgroup修改（如任务迁移和控制器开/关）的延迟，代价是使分叉和出口等热路径操作更加昂贵。创建一个cgroup，启用控制器，然后用CLONE_INTO_cgroup对其进行种子设定的静态使用模式不受此选项的影响。

memory_localevents

只使用当前cgroup的数据填充memory.events，而不填充任何子树。这是遗留行为，没有此选项的默认行为是包括子树计数。此选项是系统范围的，只能在装载时设置，也只能通过从init命名空间重新装载进行修改。在非init命名空间装载上会忽略mount选项。

memory_recursiveprot

递归地将memory.min和memory.low保护应用于整个子树，而不需要显式向下传播到叶cgroups中。这允许保护整个子树彼此不受影响，同时保留这些子树内的自由竞争。这本应是默认行为，但却是一个挂载选项，以避免依赖于原始语义的设置倒退（例如，在更高的树级别指定高得离谱的“绕过”保护值）。

## cgroups的用途:

主要有4个:

- Resource limitation: 限制资源使用，例：内存使用上限/cpu的使用限制
    
- Prioritization: 优先级控制，例：CPU利用/磁盘IO吞吐
    
- Accounting: 一些审计或一些统计
    
- Control: 挂起进程/恢复执行进程
    

### 做实验之前确定内核已经开启了cgroup功能：

```bash
[root@server1 local]# cat /boot/config-5.14.0-162.6.1.el9_1.0.1.x86_64 | grep -i cgroupCONFIG_CGROUPS=yCONFIG_BLK_CGROUP=yCONFIG_CGROUP_WRITEBACK=y......略# CONFIG_BLK_CGROUP_IOCOST is not set# CONFIG_BLK_CGROUP_IOPRIO is not set# CONFIG_BFQ_CGROUP_DEBUG is not setCONFIG_NETFILTER_XT_MATCH_CGROUP=mCONFIG_NET_CLS_CGROUP=yCONFIG_CGROUP_NET_PRIO=yCONFIG_CGROUP_NET_CLASSID=y
```

说明：CONFIG_CGROUPS=y 表示已开启cgroup

### 再确定cgroup的版本

cgroup目前存在v1/v2 两个版本，

v2 版本与v1相比,在目录组织上更清晰，管理更方便，

如何检查当前内核版本是否支持cgroup v2?

方法是:查看文件系统是否支持cgroup2

```bash
[root@server1 local]# cat /proc/filesystems | grep cgroupnodev	cgroupnodev	cgroup2
```

如果看到cgroup2，表示支持cgroup v2

### cgroup的挂载点

```bash
[root@server1 local]# mount | grep cgroupcgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot)
```

这里可以看到RHEL和Rocky只采用cgroup2版本，这里也是区别，cgroup1版本目录结构非常的多，cgroup2版本目录仅有一个。

注意:/sys/fs/cgroup的挂载方式是ro,表示readonly

因为/sys/fs/cgroup 目录由 systemd 在系统启动的过程中挂载,

它把目录挂载为只读的类型，这个目录下不能再手动创建目录

### 列出子系统

```bash
[root@server1 local]# ls /sys/fs/cgroup/cgroup.controllers      cpuset.mems.effective  memory.statcgroup.max.depth        cpu.stat               misc.capacitycgroup.max.descendants  dev-hugepages.mount    sys-fs-fuse-connections.mountcgroup.procs            dev-mqueue.mount       sys-kernel-config.mountcgroup.stat             init.scope             sys-kernel-debug.mountcgroup.subtree_control  io.pressure            sys-kernel-tracing.mountcgroup.threads          io.stat                system.slicecpu.pressure            memory.numa_stat       user.slicecpuset.cpus.effective   memory.pressure
```

也可以通过/proc/cgroups来查看

```bash
[root@server1 local]# cat /proc/cgroups #subsys_name	hierarchy	num_cgroups	enabledcpuset			0	80	1cpu				0	80	1cpuacct			0	80	1blkio			0	80	1memory			0	80	1devices			0	80	1freezer			0	80	1net_cls			0	80	1perf_event		0	80	1net_prio		0	80	1hugetlb			0	80	1pids			0	80	1rdma			0	80	1misc			0	80	1
```

各个子系统的说明：

1. cpuset:把任务绑定到特定的cpu
2. cpu:    限定cpu的时间份额
3. cpuacct: 统计一组task占用cpu资源的报告
4. blkio:限制控制对块设备的读写
5. memory:  限制内存使用
6. devices: 限制设备文件的创建\限制对设备文件的读写
7. freezer: 暂停/恢复cgroup中的task
8. net_cls: 用classid标记该cgroup内的task产生的报文
9. perf_event: 允许perf监控cgroup的task数据
10. net_prio: 设置网络流量的优先级
11. hugetlb:  限制huge page 内存页数量
12. pids:   限制cgroup中可以创建的进程数
13. rdma:  限制RDMA资源(Remote Direct Memory Access，远程直接数据存取)

这里也发现了cgroup1和cgroup2的很大不同。主要的就是目录结构的不相同，cgroup这里面的目录结构是以子系统的名字命名的。cgroup2的是进程为目录结构的，统一都存放在/sys/fs/cgroup/system.slice 的目录中。

各slice的说明：

-.slice： 根slice

- **system.slice** —— 所有系统 service 的默认位置
    
- **user.slice** —— 所有用户会话的默认位置。每个用户会话都会在该 slice 下面创建一个子 slice，如果同一个用户多次登录该系统，仍然会使用相同的子 slice。
    
- **machine.slice** —— 所有虚拟机和 Linux 容器的默认位置
    
    注意：最后一项machine.slice已经在最新版本的内核中取消了。这里我们并不会查看到。
    

什么是slice:一组进程:由service或会话/容器/虚拟机组成

### 查看一个进程上的cgroup限制

这里我们还是以httpd服务为例：

需要先查一下httpd的PID进程：

```bash
[root@server1 local]# pidof httpd       #查看进程的所有子进程pid1791 1790 1789 1788 1787[root@server1 local]# pidof -s httpd    #查看主进程pid1791[root@server1 local]# ps aux | grep httpdroot        1787  0.0  0.5  20332 11632 ?        Ss   00:47   0:00 /usr/sbin/httpd -DFOREGROUNDapache      1788  0.0  0.3  21660  7408 ?        S    00:47   0:00 /usr/sbin/httpd -DFOREGROUNDapache      1789  0.0  0.7 1669360 15176 ?       Sl   00:47   0:02 /usr/sbin/httpd -DFOREGROUNDapache      1790  0.0  0.8 1538224 17220 ?       Sl   00:47   0:02 /usr/sbin/httpd -DFOREGROUNDapache      1791  0.0  0.5 1538224 11088 ?       Sl   00:47   0:02 /usr/sbin/httpd -DFOREGROUNDroot        2192  0.0  0.1   6408  2220 pts/0    S+   02:03   0:00 grep --color=auto httpd
```

能查看到cgroup的方法很多：

```bash
[root@server1 local]# ps -o cgroup 1791CGROUP0::/system.slice/httpd.service[root@server1 local]# cat /proc/1791/cgroup 0::/system.slice/httpd.service[root@server1 local]# systemctl status 1791 | grep -i cgroup     CGroup: /system.slice/httpd.service
```

这里的正确的物理路径为:

```bash
[root@server1 local]# ls /sys/fs/cgroup/system.slice/httpd.service/cgroup.controllers      cpuset.cpus.effective  memory.lowcgroup.events           cpuset.cpus.partition  memory.maxcgroup.freeze           cpuset.mems            memory.mincgroup.kill             cpuset.mems.effective  memory.numa_statcgroup.max.depth        cpu.stat               memory.oom.groupcgroup.max.descendants  cpu.weight             memory.pressurecgroup.procs            cpu.weight.nice        memory.statcgroup.stat             io.bfq.weight          memory.swap.currentcgroup.subtree_control  io.latency             memory.swap.eventscgroup.threads          io.max                 memory.swap.highcgroup.type             io.pressure            memory.swap.maxcpu.idle                io.stat                pids.currentcpu.max                 memory.current         pids.eventscpu.max.burst           memory.events          pids.maxcpu.pressure            memory.events.localcpuset.cpus             memory.high
```

cgroup2的所有配置文件都存放在这一个地方了。

从RHEL8开始增加了一个比较有趣的命令，可以直接查看每个进程的cgroup所消耗资源的大小：

```bash
[root@server1 local]# systemd-cgtopControl Group                            Tasks   %CPU   Memory  Input/s Output/s/                                          459      -   768.6M        -        -dev-hugepages.mount                          -      -    28.0K        -        -dev-mqueue.mount                             -      -     4.0K        -        -......略system.slice/containerd.service              9      -    61.7M        -        -system.slice/crond.service                   1      -     1.1M        -        -system.slice/dbus-broker.service             2      -     2.3M        -        -
```

还可以直接查看cgroup的目录层级结构：

```bash
[root@server1 local]# systemd-cglsControl group /:-.slice├─user.slice (#1196)│ → trusted.invocation_id: 199df5159c1147a3a4ecf54380f3a342│ └─user-0.slice (#4106)│ → trusted.invocation_id: 7fd25cd90859471a9d436aefea553fe6│ ├─session-1.scope (#4337)│ │ ├─1387 sshd: root [priv]│ │ ├─1398 sshd: root@pts/0│ │ ├─1399 -bash......略
```

当然这条命令可以直接切换到对应的目录也可以直接查看:

```bash
[root@server1 httpd.service]# systemd-cglsWorking directory /sys/fs/cgroup/system.slice/httpd.service:├─1900 /usr/sbin/httpd -DFOREGROUND├─1901 /usr/sbin/httpd -DFOREGROUND├─1902 /usr/sbin/httpd -DFOREGROUND├─1903 /usr/sbin/httpd -DFOREGROUND└─1904 /usr/sbin/httpd -DFOREGROUND
```

## 设置之前认识一下什么是进程和线程

### cgroup.procs

给定的cgroup可以具有多个子cgroup，这些子cgroup形成树结构。每个cgroup都有一个可读写的接口文件“cgroup.procs”。读取时，它每行列出属于该cgroup的所有进程的PID。PID没有排序，如果进程被移动到另一个cgroup，然后返回，或者PID在读取时被回收，则同一PID可能会多次显示。

通过将进程的PID写入目标cgroup的“cgroup.procs”文件，可以将进程迁移到cgroup中。一次写入调用只能迁移一个进程。如果一个进程由多个线程组成，那么写入任何线程的PID都会迁移该进程的所有线程。

当一个进程分叉一个子进程时，新进程会在操作时生成到分叉进程所属的cgroup中。退出后，进程将与退出时所属的cgroup保持关联，直到它被收割；然而，僵尸进程不会出现在“cgroup.prcs”中，因此无法移动到另一个cgroup。

没有任何子级或活动进程的cgroup可以通过删除目录来销毁。请注意，一个没有任何子级并且只与僵尸进程关联的cgroup被认为是空的，可以删除.  
“/proc/$PID/cgroup”列出进程的cgroup成员身份。如果系统中正在使用旧式cgroup，则此文件可能包含多行，每个层次结构一行。cgroup v2的条目始终采用“0:：$PATH”格式：

以刚才的httpd为例:

```bash
[root@server1 httpd.service]# cat cgroup.procs19001901190219031904
```

这里显示的就是httpd所有的进程和子进程的pid.

### cgroup.type

cgroupv2支持控制器子集的线程粒度，以支持需要跨一组进程的线程进行分层资源分配的用例。默认情况下，进程的所有线程都属于同一个cgroup，该cgroup还充当资源域来承载非进程或线程特定的资源消耗。线程模式允许线程分布在子树中，同时仍然为它们维护公共资源域。

支持线程模式的控制器称为线程控制器。那些不被称为域控制器的。

将cgroup标记为线程化使其作为线程化cgroup加入其父级的资源域。父级可以是另一个线程cgroup，其资源域在层次结构中更靠上。带线程子树的根，即最近的未带线程的祖先，可互换地称为线程域或线程根，并作为整个子树的资源域。

在线程子树中，进程的线程可以放在不同的cgroup中，并且不受无内部进程约束的约束——线程控制器可以在非叶cgroup上启用，无论它们中是否有线程。

由于线程域cgroup承载子树的所有域资源消耗，因此无论其中是否有进程，它都被认为具有内部资源消耗，并且不能填充未线程化的子cgroup。因为根cgroup不受任何内部进程约束，所以它既可以作为线程域，也可以作为域cgroups的父级。

cgroup.type文件中显示了cgroup的当前操作模式或类型，该文件指示cgroup是普通域、用作线程子树域的域还是线程cgroup。

在创建时，cgroup始终是域cgroup，可以通过将“thread”写入“cgroup.type”文件来实现线程化。操作是单向的, 这里展示一下语法

```bash
# echo threaded > cgroup.type
```

一旦线程化，cgroup就不能再次成为域。要启用线程模式，必须满足以下条件。

1. 因为cgroup将加入父级的资源域。父级必须是有效的（线程化的）域或线程化的cgroup。
2. 当父域是无线程域时，它不能启用任何域控制器或填充域子域。根不受此要求的约束。

```bash
A (threaded domain) - B (threaded) - C (domain, just created)
```

C被创建为一个域，但没有连接到可以承载子域的父域。在将C转换为线程化的cgroup之前，不能使用它。在这些情况下，“cgroup.type”文件将报告“域（无效）”。由于拓扑无效而失败的操作使用EOPNOTSUPP作为错误号。

当域cgroup的一个子cgroup变为线程化时，或者在“cgroup.subtree_control”文件中启用了线程控制器，而cgroup中有进程时，该域cggroup将变为线程域。当条件清除时，线程域将恢复为正常域。

读取时，“cgroup.threads”包含cgroup中所有线程的线程ID列表。除了操作是按线程而不是按进程进行外，“cgroup.threads”具有与“cgroup.procs”相同的格式和行为方式。虽然“cgroup.threads“可以在任何cgroup中写入，因为它只能在同一线程域内移动线程，但它的操作被限制在每个线程子树内。

线程域cgroup充当整个子树的资源域，虽然线程可以分散在子树上，但所有进程都被认为在线程域cggroup中。线程域中的“cgroup.procs”cgroup包含子树中所有进程的PID，在子树中是不可读的。但是，可以从子树中的任何位置写入“cgroup.procs”，以将匹配进程的所有线程迁移到cgroup。

在线程子树中只能启用线程控制器。当在线程子树中启用线程控制器时，它只考虑并控制与cgroup及其子代中的线程相关联的资源消耗。所有未绑定到特定线程的消耗都属于线程域cgroup。

因为线程子树不受任何内部进程约束，所以线程控制器必须能够处理非叶cgroup中的线程与其子cgroup之间的竞争。每个线程控制器都定义了如何处理此类竞争。

下面看看例子:

```bash
[root@server1 httpd.service]# cat cgroup.typedomain[root@server1 httpd.service]# cat cgroup.eventspopulated 1frozen 0[root@server1 httpd.service]# cat cgroup.threads1900190119021903.......略
```

每个非根cgroup都有一个“cgroup.events”文件，其中包含“已填充”字段，指示cgroup的子层次结构中是否有活动进程。如果cgroup及其子代中没有活动进程，则其值为0；否则，1。当值更改时，会触发poll和[id]notify事件。例如，这可以用于在给定子层次结构的所有进程退出后启动清理操作。填充的状态更新和通知是递归的。考虑以下子层次结构，其中括号中的数字表示每个cgroup中的进程数：

```bash
A(4) - B(0) - C(1)            \ D(0)
```

A、 B和C的“填充”字段将为1，而D的字段为0。在C中的一个进程退出后，B和C的“已填充”字段将翻转到“0”，并且文件修改事件将在两个cgroup.events文件上生成。

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#%E9%82%A3%E4%B9%88rhel9%E7%9A%84cgroup%E8%AE%BE%E7%BD%AE%E5%8F%82%E6%95%B0%E6%96%87%E4%BB%B6%E9%83%BD%E8%A1%A8%E7%A4%BA%E4%BB%80%E4%B9%88%E6%84%8F%E6%80%9D)那么RHEL9的cgroup设置参数文件都表示什么意思

每个cgroup都有一个“cgroup.controllers”文件，该文件列出了cgroup可启用的所有控制器：

```bash
[root@server1 httpd.service]# cat cgroup.controllerscpuset cpu io memory pids
```

默认情况下未启用任何控制器。可以通过写入“cgroup.subtree_control”文件来启用和禁用控制器：

这里注意一下, 这个参数不能直接修改, 启动程序后就无法设置了, 只有自己的手动创建cgroup的时候才可以, 或者程序开发阶段的设置.

```bash
[root@server1 httpd.service]# echo "+cpu +memory -io" > cgroup.subtree_control-bash: echo: write error: Device or resource busy
```

只能启用“cgroup.controllers”中列出的控制器。当如上所述指定多个操作时，它们要么全部成功，要么全部失败。如果在同一控制器上指定了多个操作，则最后一个操作有效。  
启用cgroup中的控制器表示将控制目标资源在其直属子级之间的分布。考虑以下子层次结构。括号中列出了启用的控制器：

```bash
A(cpu,memory) - B(memory) - C()                          \ D()
```

由于A启用了“cpu”和“内存”，A将控制cpu周期和内存分配给它的子级，在这种情况下，B。由于B启用了“内存”但没有启用“cpu”，C和D将在cpu周期上自由竞争，但它们对B可用内存的分配将受到控制。

当控制器调节目标资源到cgroup的子级的分配时，启用它会在子cgroups中创建控制器的接口文件。在上面的例子中，在B上启用“cpu”将在C和D中创建前缀为“cpu.”的控制器接口文件。同样，从B禁用“memory”将从C和D删除前缀为“memory.”的控制器界面文件。这意味着控制器接口文件-任何不以“cgroup.”开头的文件都归父级所有，而不是cgroup本身。

自上而下约束

资源是自上而下分布的，只有从父级向cgroup分配了资源，cgroup才能进一步分布资源。这意味着所有非根的“cgroup.subtree_control”文件只能包含在父级的“cggroup.subtree_control”文件中启用的控制器。只有当父级启用了控制器时，才能启用控制器；如果一个或多个子级启用了该控制器，则不能禁用该控制器。

```bash
[root@server1 httpd.service]# cat cgroup.subtree_control
```

无内部流程约束

非根cgroups只有在没有自己的进程时，才能将域资源分发给其子级。换句话说，只有不包含任何进程的域cgroups才能在其“cgroup.subtree_control”文件中启用域控制器。

这保证了，当域控制器查看层次结构中启用它的部分时，进程总是只在叶子上。这排除了子cgroup与父cgroup的内部进程竞争的情况。

根cgroup不受此限制。根包含无法与任何其他cgroup关联的进程和匿名资源消耗，并且需要大多数控制器进行特殊处理。如何管理根cgroup中的资源消耗取决于每个控制器（有关此主题的更多信息，请参阅控制器一章中的非规范性信息部分）。

==请注意，如果cgroup的“cgroup.subtree_control”中没有启用的控制器，则限制不会成为障碍==。这一点很重要，因为否则将无法创建已填充的cgroup子级。要控制cgroup的资源分布，cgroup必须创建子级并将其所有进程传输给子级，然后才能在其“cgroup.subtree_control”文件中启用控制器。

授权模式

一个cgroup可以通过两种方式进行委派。首先，通过将目录及其“cgroup.procs”、“cgroup.threads”和“cgroup.subtree_control”文件的写访问权限授予权限较低的用户。其次，如果设置了“nsdelegate”装载选项，则在创建命名空间时自动将其设置为cgroup命名空间。

由于给定目录中的资源控制接口文件控制父级资源的分布，因此不应允许被委派者写入这些文件。对于第一种方法，这是通过不授予对这些文件的访问权限来实现的。对于第二个，内核拒绝从命名空间内部写入命名空间根上除“cgroup.procs”和“cgroup.subtree_control”之外的所有文件。

两种委托类型的最终结果都是等效的。一旦被委托，用户就可以在目录下建立子层次结构，根据自己的意愿组织其中的流程，并进一步分配从父目录接收的资源。所有资源控制器的限制和其他设置都是分层的，无论委托的子层次结构中发生了什么，都无法逃脱父级施加的资源限制。

目前，cgroup对委托子层次结构中的cgroup数量或嵌套深度没有任何限制；然而，这在未来可能会受到明确的限制。

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#%E9%81%BF%E5%85%8D%E5%90%8D%E7%A7%B0%E5%86%B2%E7%AA%81)避免名称冲突

cgroup及其子cgroup的接口文件占用相同的目录，并且可以创建与接口文件冲突的子cgroups。

所有cgroup核心接口文件都以“cgroup”为前缀，每个控制器的接口文件都用控制器名称和一个点作为前缀。控制器的名称由小写字母和“_”组成，但从不以“_”开头，因此可以用作避免冲突的前缀字符。此外，接口文件名不会以常用于对工作负载（如作业、服务、切片、单元或工作负载）进行分类的术语开头或结尾。

cgroup不会采取任何措施来防止名称冲突，用户有责任避免这些冲突。

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#%E8%B5%84%E6%BA%90%E5%88%86%E9%85%8D%E6%A8%A1%E5%BC%8F)资源分配模式

cgroup控制器根据资源类型和预期用例实现了几种资源分配方案。本节描述了正在使用的主要方案及其预期行为。

**权重 weights**

通过将所有活动子项的权重相加，并给出与其权重与总和之比相匹配的分数，来分配父项的资源。由于目前只有能够利用资源的儿童才能参与分配，这是节约工作。由于其动态性，该模型通常用于无状态资源。

所有权重都在[1,10000]的范围内，默认值为100。这允许在两个方向上以足够精细的粒度进行对称乘法偏置，同时保持在直观的范围内。

只要权重在范围内，所有配置组合都是有效的，没有理由拒绝配置更改或进程迁移。

“cpu.weight”按比例将cpu周期分配给活动的子级，就是这种类型的一个例子。

```bash
[root@server1 httpd.service]# cat cpu.weight100
```

**限制 limits**

子级最多只能消耗配置数量的资源。限制可能被过度承诺-子项限制的总和可能超过父项可用的资源量。

限制在[0，max]范围内，默认为“max”，即noop。

由于限制可能被过度提交，所有配置组合都是有效的，没有理由拒绝配置更改或处理迁移。

“io.max”限制了cgroup在io设备上可以消耗的最大BPS和/或IOPS，就是这种类型的一个例子, 默认没有任何值即没有限制.

```bash
[root@server1 httpd.service]# cat io.max
```

**保护 protections**

只要一个cgroup的所有起始进程的使用都在其受保护级别之下，它就会受到资源配置量的保护。保护可以是硬保证，也可以是尽最大努力的软边界。保护也可能被过度承诺，在这种情况下，只有父进程可用的数量才能在子进程之间得到保护。

保护 在[0，max]范围内，默认为0，即noop。

由于保护可能被过度提交，因此所有配置组合都是有效的，没有理由拒绝配置更改或处理迁移。

“memory.low”实现了尽力而为的内存保护，就是这种类型的一个例子。

```bash
[root@server1 httpd.service]# cat memory.low0
```

**分配 Allocations**

一个cgroup被独占地分配了一定数量的有限资源。分配不能超额提交-子级分配的总和不能超过父级可用的资源量。

分配在[0，max]范围内，默认为0，这不是资源。

由于分配不能被过度提交，一些配置组合是无效的，应该被拒绝。此外，如果资源对于进程的执行是强制性的，那么进程迁移可能会被拒绝。

“cpu.rt.max”硬分配实时切片，就是这种类型的一个例子。

```bash
[root@server1 httpd.service]# cat cpu.maxmax 100000
```

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#%E8%AE%BE%E7%BD%AE%E7%9A%84%E9%80%9A%E7%94%A8%E8%A7%84%E5%88%99)设置的通用规则

- 单个功能的设置应包含在单个文件中。
    
- 根cgroup应该不受资源控制，因此不应该有资源控制接口文件。
    
- 默认的时间单位是微秒。如果使用不同的单位，则必须存在明确的单位后缀。
    
- 每个数量的部分应使用小数百分比，小数部分至少为两位数，例如13.40。
    
- 如果一个控制器实现基于权重的资源分配，那么它的接口文件应该命名为“weight”，并且范围为[110000]，默认值为100。选择这些值以允许在两个方向上有足够的对称偏差，同时保持直观（默认值为100%）。
    
- 如果控制器实现了绝对的资源保证和/或限制，则接口文件应分别命名为“min”和“max”。如果控制器实现尽最大努力的资源保证和/或限制，则接口文件应分别命名为“low”和“high”。
    
- 在上面的四个控制文件中，应该使用特殊的标记“max”来表示向上的无穷大，用于读取和写入。
    
- 如果设置具有可配置的默认值和键控的特定覆盖，则默认条目应使用“default”键控，并显示为文件中的第一个条目。
    

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#%E8%AF%AD%E6%B3%95)语法

可以通过写入“default$VAL”或“$VAL”来更新默认值。

当写入以更新特定的覆盖时，“默认”可以用作指示删除覆盖的值。使用“default”覆盖条目，因为读取时不得显示值。

例如，由具有整数值的主要：次要设备编号键入的设置可能如下所示：

在/tmp目录下随便建一个文件演示一下:

```bash
[root@server1 tmp]# cat cgroup-example-interface-filedefault 15080:0 300
```

默认值可以通过以下方式更新：

```bash
[root@server1 tmp]# echo 125 > cgroup-example-interface-file
```

或者

```bash
[root@server1 tmp]# echo "default 125" > cgroup-example-interface-file
```

可以通过以下方式设置覆盖：

```bash
[root@server1 tmp]# echo "8:16 170" > cgroup-example-interface-file
```

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#cgroup%E7%9A%84%E6%A0%B8%E5%BF%83%E6%8E%A5%E5%8F%A3%E6%96%87%E4%BB%B6%E5%86%85%E5%AE%B9)cgroup的核心接口文件内容

所有cgroup核心文件都以“cgroup”为前缀

cgroup类型

存在于非根cgroups上的读写单值文件。

读取时，它指示cgroup的当前类型，可以是以下值之一。

1. “domain”：一个正常有效的域cgroup。
    
2. “domain threaded”：作为线程子树根的线程域cgroup。
    
3. “domain invalid”：处于无效状态的cgroup。无法填充或启用控制器。它可以被允许成为一个线程cgroup。
    
4. “threaded”：一个线程化的cgroup，它是一个线程子树的成员。
    

通过将“线程化”写入该文件，可以将cgroup转换为线程化cgroup。

**cgroup.procs**

一个存在于所有cgroup上的读写新行分隔值文件。

读取时，它每行列出一个属于cgroup的所有进程的PID。PID没有排序，如果进程被移动到另一个cgroup，然后返回，或者PID在读取时被回收，则同一PID可能会多次显示。

**cgroup.threads**

一个存在于所有cgroup上的读写新行分隔值文件。

读取时，它每行列出一个属于cgroup的所有线程的TID。TID没有排序，如果线程被移到另一个cgroup，然后又移回来，或者TID在读取时被回收，那么同一个TID可能会出现不止一次。

**cgroup.controllers**

一个只读的以空格分隔的值文件，存在于所有cgroup上。

它显示了cgroup可用的所有控制器的空格分隔列表。控制器未排序。

**cgroup.subtree_control**

一个读写空间分隔的值文件，存在于所有cgroup上。一开始是空的。

读取时，它会显示控制器的空格分隔列表，这些控制器可以控制从cgroup到其子组的资源分配。

可以写入以“+”或“-”为前缀的以空格分隔的控制器列表，以启用或禁用控制器。前缀为“+”的控制器名称启用控制器，而“-”禁用。如果一个控制器在列表上出现多次，则最后一个控制器有效。当指定了多个启用和禁用操作时，要么全部成功，要么全部失败。

**cgroup.events**

存在于非根cgroups上的只读平面键控文件。定义了以下条目。除非另有规定，否则此文件中的值更改将生成文件修改事件。

密集的populated: 如果cgroup或其子代包含任何活动进程，则为1；否则为0。

冻结的frozen: 如果cgroup被冻结，则为1；否则为0。

```bash
[root@server1 httpd.service]# cat cgroup.eventspopulated 1frozen 0
```

**cgroup.max.descendants**

一个读写的单值文件。默认值为“最大值”。

cgroups的最大允许数量。如果子进程的实际数量等于或大于，则尝试在层次结构中创建新的cgroup将失败。

```bash
[root@server1 httpd.service]# cat cgroup.max.descendantsmax
```

max 不受限制

**cgroup.max.depth**

一个读写的单值文件。默认值为“最大值”。

当前cgroup下方允许的最大下降深度。如果实际下降深度等于或大于，则尝试创建新的子cgroup将失败。

```bash
[root@server1 httpd.service]# cat cgroup.max.depthmax
```

**cgroup.stat**

具有以下条目的只读平面键控文件：

nr_descendants: 可见子代cgroups的总数。

nr_dying_descendants: 垂死的后代cgroups的总数。一个cgroup在被一个用户删除后，就会死亡。在被完全销毁之前，cgroup将在一段时间内保持垂死状态——未定义的时间（这可能取决于系统负载）。

进程在任何情况下都不能进入垂死的cgroup，垂死的cggroup也不能复活。

垂死的cgroup可以消耗不超过限制的系统资源，这些资源在cgroup删除时是活动的。

```bash
[root@server1 httpd.service]# cat cgroup.statnr_descendants 0nr_dying_descendants 0
```

**cgroup.freeze**

存在于非根cgroups上的读写单值文件。允许的值为“0”和“1”。默认值为“0”。

将“1”写入文件会导致cgroup和所有子代cgroup冻结。这意味着所有属于的进程都将停止，并且在cgroup被显式解冻之前不会运行。冻结cgroup可能需要一些时间；此操作完成后，cgroup.events控制文件中的“冻结”值将更新为“1”，并发出相应的通知。

一个cgroup可以通过它自己的设置冻结，也可以通过任何祖先cgroup的设置冻结。如果任何祖先cgroups被冻结，则该cgroup将保持冻结状态。

冻结的cgroup中的进程可能会被致命信号杀死。他们也可以进入和离开一个冻结的cgroup：要么通过用户的显式移动，要么如果cgroup的冻结与fork（）竞争。如果一个进程被移动到一个冻结的cgroup，它就会停止。如果一个进程从冻结的cgroup中移出，它就开始运行。

cgroup的冻结状态不会影响任何cgroup树操作：可以删除冻结的（空的）cgroup，也可以创建新的子cgroup。

```bash
[root@server1 httpd.service]# cat cgroup.freeze0
```

**cgroup.kill**

存在于非根cgroups中的只写单值文件。唯一允许的值是“1”。

将“1”写入文件会导致cgroup和所有子代cgroup被终止。这意味着位于受影响的cgroup树中的所有进程都将通过SIGKILL终止。

杀死一个cgroup树将适当地处理并发分叉，并防止迁移。

在线程cgroup中，使用EOPNOTSUPP写入此文件失败，因为杀死cgroups是一个进程导向的操作，即它会影响整个线程组。

```bash
[root@server1 httpd.service]# cat cgroup.killcat: cgroup.kill: Invalid argument
```

唯一值得禁止修改

**cgroup.pressure**

允许值为“0”和“1”的读写单值文件。默认值为“1”。

将“0”写入文件将禁用cgroup PSI记帐。将“1”写入文件将重新启用cgroup PSI记帐。

此控制属性不是分层的，因此在cgroup中禁用或启用PSI记帐不会影响后代中的PSI记帐，也不需要从根通过祖先传递启用。

之所以存在此控制属性，是因为PSI分别为每个cgroup暂停，并在层次结构的每个级别聚合它。当处于层次结构的深层时，这可能会对某些工作负载造成不可忽略的开销，在这种情况下，可以使用此控制属性来禁用非叶cgroups中的PSI记帐。

```bash
rockylinux 9 默认没有启动, 独立开发时候添加即可
```

**irq.pressure**

一种读写嵌套键控文件。

显示IRQ/SOFTIRQ的压力失速信息。有关详细信息，请参阅kernel官网的Documentation/accounting/pis.rst。

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#cpu%E8%AE%BE%E7%BD%AE%E9%80%89%E9%A1%B9)CPU设置选项

“cpu”控制器调节cpu周期的分布。该控制器实现了正常调度策略的权重和绝对带宽限制模型以及实时调度策略的绝对带宽分配模型。

在所有上述模型中，周期分布仅在时间基础上定义，并且它不考虑执行任务的频率。（可选）利用率箝位支持允许向schedutil cpufreq调速器提示应始终由CPU提供的最小期望频率，以及CPU不应超过的最大期望频率。

警告：cgroup2还不支持对实时进程的控制，并且只有当所有RT进程都在根cgroup中时，才能启用cpu控制器。请注意，在系统引导过程中，系统管理软件可能已经将RT进程放置到非根cgroup中，并且在启用cpu控制器之前，这些进程可能需要移动到根cggroup。

==所有持续时间均以微秒为单位。==

**cpu.stat**

只读的平面键控文件。无论控制器是否启用，此文件都存在。

它总是报告以下三个统计数据：

- usage_usec
- user_usec
- system_usec

以及当控制器被启用时的以下三个：

- nr_periods
- nr_throttled
- throttled_usec
- nr_bursts
- burst_usec

**cpu.weight**

存在于非根cgroups上的读写单值文件。默认值为“100”。

在[1,10000]范围内的权重。

```bash
[root@server1 httpd.service]# cat cpu.weight100
```

**cpu.weight.nice**

存在于非根cgroups上的读写单值文件。默认值为“0”。

不错的值在[-20，19]的范围内。

这个接口文件是“cpu.weight”的替代接口，允许使用nice（2）使用的相同值读取和设置权重。由于漂亮值的范围较小，粒度较粗，因此读取值是当前权重的最接近值。

```bash
[root@server1 httpd.service]# cat cpu.weight.nice0
```

**cpu.max**

存在于非根cgroups上的读写双值文件。默认值为“max 100000”。

最大带宽限制。它的格式如下：

```bash
$MAX $PERIOD
```

这指示该组可以在每个$PERIOD持续时间中消耗高达$MAX。$max的“max”表示没有限制。如果只写入一个数字，则$MAX将被更新。

```bash
[root@server1 httpd.service]# cat cpu.maxmax 100000
```

**cpu.max.burst**

存在于非根cgroups上的读写单值文件。默认值为“0”。

在[0，$MAX]范围内的突发。

```bash
[root@server1 httpd.service]# cat cpu.max.burst0
```

**cpu.pressure **

一种读写嵌套键控文件。

显示CPU的压力失速信息。有关详细信息，请参阅官网Documentation/accounting/pis.rst。

```bash
[root@server1 httpd.service]# cat cpu.pressurecat: cpu.pressure: Operation not supported
```

默认无权查看

**cpu.uclamp.min 默认没有这个选项**

存在于非根cgroups上的读写单值文件。默认值为“0”，即没有提高利用率。

要求的最低利用率（保护）是一个合理的百分比，例如12.34%为12.34。

该接口允许读取和设置类似于sched_setattr（2）的最小利用率箝位值。该最小利用率值用于钳制任务特定的最小利用率钳制。

请求的最小利用率（保护）总是由最大利用率（限制）的当前值来限制，即cpu.uclamp.max。

**cpu.uclamp.max 默认没有这个选项**

存在于非根cgroups上的读写单值文件。默认值为“最大值”。即没有使用上限

请求的最大利用率（限制），以百分比有理数表示，例如98.76表示98.76%。

该接口允许读取和设置与sched_setattr（2）类似的最大利用率箝位值。此最大利用率值用于钳制任务特定的最大利用率钳制。

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#memory)Memory

“内存”控制器调节内存的分配。内存是有状态的，同时实现了限制和保护模型。由于内存使用和回收压力以及内存的状态性之间的交织，分布模型相对复杂。

虽然不是完全限制，但会跟踪给定cgroup的所有主要内存使用情况，以便在合理的范围内计算和控制总内存消耗。目前，跟踪以下类型的内存使用情况。

- Userland memory页面缓存和匿名内存。
    
- 内核数据结构，如dentries和inode。
    
- CP socket buffers.
    

所有内存量均以字节为单位。如果写入了与PAGE_SIZE不对齐的值，则在读回时，该值可以四舍五入到最接近的PAGE_SIZE倍数。

**memory.current**

存在于非根cgroups上的只读单值文件。

cgroup及其子代当前正在使用的内存总量。

```bash
[root@server1 httpd.service]# cat memory.current37642240
```

**memory.min**

存在于非根cgroups上的读写单值文件。默认值为“0”。

限制内存使用。如果cgroup的内存使用量在其有效最小边界内，则在任何情况下都不会回收cgroup内存。如果没有不受保护的可回收内存可用，就会调用OOM杀手。在有效最小边界（或有效低边界，如果更高）以上，页面将按比例回收，以减少较小超额的回收压力。

有效最小边界受到所有祖先cgroups的memory.min值的限制。如果存在memory.min过度委托（子cgroup或cgroups需要的受保护内存比父cgroup允许的要多），则每个子cgroups将获得与其实际内存使用量成比例的父保护部分，低于memory.min。

不鼓励将比通常可用的内存更多的内存置于这种保护之下，并可能导致持续的OOM。

如果内存cgroup未填充进程，则会忽略其memory.min。

```bash
[root@server1 httpd.service]# cat memory.min0
```

**memory.low**

存在于非根cgroups上的读写单值文件。默认值为“0”。

尽力保护内存。如果cgroup的内存使用率在其有效的低边界内，则除非在未受保护的cgroups中没有可用的可回收内存，否则不会回收cgroup内存。在有效的低边界（或有效的最小边界，如果它更高）以上，页面将按比例回收，以减少较小超额的回收压力。

有效的低边界受到内存的限制。所有祖先cgroups的值都很低。如果存在memory.low过度承诺（子cgroup或cgroups需要比父cgroup允许的更多的受保护内存），则每个子cgroups将获得与其实际内存使用量成比例的父保护部分，低于memory.low。

不鼓励将比通常可用的内存更多的内存置于这种保护之下。

```bash
[root@server1 httpd.service]# cat memory.low0
```

**memory.high**

存在于非根cgroups上的读写单值文件。默认值为“最大值”。

内存使用限制。这是控制cgroup内存使用的主要机制。如果一个cgroup的使用量超过了上限，那么该cgroup中的进程就会受到抑制，并承受巨大的回收压力。

超过上限永远不会引发OOM杀手，在极端条件下，可能会突破上限。

```bash
[root@server1 httpd.service]# cat memory.highmax
```

**memory.max**

存在于非根cgroups上的读写单值文件。默认值为“最大值”。

内存使用硬性限制。这是最后的保护机制。如果一个cgroup的内存使用量达到了这个极限并且无法减少，那么就会在cgroup中调用OOM杀手。在某些情况下，使用量可能会暂时超过限制。

在默认配置中，常规的0阶分配总是成功的，除非OOM杀手选择当前任务作为牺牲品。

某些类型的分配不会调用OOM杀手。调用方可以以不同的方式重试，以-ENOMM的形式返回用户空间，或者在磁盘预读等情况下静默忽略。

这是最终的保护机制。只要正确使用和监测高限值，该限值的效用仅限于提供最终的安全网。

```bash
[root@server1 httpd.service]# cat memory.maxmax
```

**memory.reclaim 默认没有启用**

一个只写嵌套键控文件，存在于所有cgroup中。

这是一个简单的接口，用于触发目标cgroup中的内存回收。

这个文件接受一个密钥，即要回收的字节数。当前不支持嵌套键。

```bash
echo "1G" > memory.reclaim
```

该接口稍后可以使用嵌套键进行扩展，以配置回收行为。例如，指定要回收的内存类型（anon、file、..）。

请注意，内核可以从目标cgroup中回收或回收不足。如果回收的字节数少于指定的数量，则返回-EAGAIN。

请注意，主动回收（由该接口触发）并不意味着指示内存cgroup上的内存压力。因此，在这种情况下，通常不会执行由内存回收触发的套接字内存平衡。这意味着网络层将不会根据memory.reclaim引起的回收进行调整。

**memory.peak**

存在于非根cgroups上的只读单值文件。

自创建cgroup以来，为cgroup及其子代记录的最大内存使用量。

**memory.oom.group**

存在于非根cgroups上的读写单值文件。默认值为“0”。

确定cgroup是否应被OOM杀手视为不可分割的工作负载。如果设置，则属于cgroup或其子代（如果内存cgroup不是叶cgroup）的所有任务都会一起终止或根本不终止。这可以用来避免部分终止，以保证工作负载的完整性。

具有OOM保护（OOM_score_adj设置为-1000）的任务被视为异常，并且永远不会被终止。

如果OOM杀手在一个cgroup中被调用，它不会杀死这个cgroup之外的任何任务，无论祖先cgroups的memory.OOM.group值如何。

```bash
[root@server1 httpd.service]# cat memory.oom.group0
```

**memory.events**

存在于非根cgroups上的只读平面键控文件。定义了以下条目。除非另有规定，否则此文件中的值更改将生成文件修改事件。

请注意，此文件中的所有字段都是层次结构的，并且由于层次结构下的事件，可以生成文件修改事件。有关cgroup级别的本地事件，请参阅memory.events.local。

```bash
[root@server1 httpd.service]# cat memory.eventslow 0high 0max 0oom 0oom_kill 0
```

low: 由于高内存压力而回收cgroup的次数，即使其使用率处于低边界以下。这通常表明低边界被过度提交。

hight: 由于超出了高内存边界，cgroup的进程被节流和路由以执行直接内存回收的次数。对于内存使用量由上限而非全局内存压力限制的cgroup，预计会发生此事件。

max: cgroup的内存使用率即将超过最大边界的次数。如果直接回收失败，则cgroup将进入OOM状态。

oom: cgroup的内存使用达到限制并且分配即将失败的时间。如果OOM killer不被视为一个选项，例如对于失败的高阶分配，或者如果调用方要求不要重试，则不会引发此事件。

oom_kill: 属于该cgroup的进程被任何类型的OOM杀手杀死的数量。

oom_group_kill: 发生组OOM的次数。

**memory.events.local**

类似于memory.events，但文件中的字段是cgroup的本地字段，即不是分层的。在此文件上生成的文件修改事件仅反映本地事件。

```bash
[root@server1 httpd.service]# cat memory.events.locallow 0high 0max 0oom 0oom_kill 0
```

**memory.stat**

存在于非根cgroups上的只读平面键控文件。

这将cgroup的内存占用分解为不同类型的内存、特定类型的详细信息以及关于内存管理系统的状态和过去事件的其他信息。

所有内存量均以字节为单位。

条目被排序为人类可读，新条目可以显示在在中间。不要依赖于保持在固定位置的物品；使用键查找特定值！

如果条目没有每个节点计数器（或没有显示在内存中。numa_stat）。我们使用“npn”（非每个节点）作为标记，表示它不会显示在内存。numa\ustat。

```bash
[root@server1 httpd.service]# cat memory.statanon 24223744file 5304320kernel 8114176kernel_stack 3473408......略 
```

这里的具体解释可以参考官网

**memory.numa_stat**

存在于非根cgroups上的只读嵌套键控文件。

这将cgroup的内存占用分解为不同类型的内存、特定类型的详细信息以及每个节点关于内存管理系统状态的其他信息。

这对于提供memcg内NUMA位置信息的可见性是有用的，因为允许从任何物理节点分配页面。其中一个用例是通过将这些信息与应用程序的CPU分配相结合来评估应用程序性能。

所有内存量均以字节为单位。

条目被排序为人类可读，新条目可以显示在在中间。不要依赖于保持在固定位置的物品；使用键查找特定值！

条目可以引用memory.stat。

```bash
[root@server1 httpd.service]# cat memory.numa_statanon N0=24223744file N0=5304320kernel_stack N0=3473408pagetables N0=1413120......略
```

**memory.swap.current**

存在于非根cgroups上的只读单值文件。

cgroup及其子代当前正在使用的交换总量。

```bash
[root@server1 httpd.service]# cat memory.swap.current0
```

**memory.swap.high**

存在于非根cgroups上的读写单值文件。默认值为“最大值”。

交换使用限制。如果一个cgroup的交换使用量超过了这个限制，那么它的所有进一步分配都将被限制，以允许用户空间实现自定义的内存不足过程。

这个限制标志着cgroup的一个不归路点。它并不是为了管理工作负载在常规操作期间进行的交换量而设计的。与memory.swap.max相比，后者禁止交换超过设定的数量，但只要其他内存可以回收，cgroup就可以不受阻碍地继续。

健康的工作负载预计不会达到这个极限。

```bash
[root@server1 httpd.service]# cat memory.swap.highmax
```

**memory.swap.max**

存在于非根cgroups上的读写单值文件。默认值为“最大值”。

交换使用硬限制。如果cgroup的交换使用量达到此限制，则不会交换出cgroup中的匿名内存。

```bash
[root@server1 httpd.service]# cat memory.swap.maxmax
```

**memory.swap.events**

存在于非根cgroups上的只读平面键控文件。定义了以下条目。除非另有规定，否则此文件中的值更改将生成文件修改事件。

```bash
[root@server1 httpd.service]# cat memory.swap.eventshigh 0max 0fail 0
```

hight: cgroup的交换使用率超过高阈值的次数。

max: cgroup的交换使用即将超过最大边界并且交换分配失败的次数。

fail: 由于交换系统范围或最大限制不足而导致交换分配失败的次数。

当在当前使用量下减少时，现有的交换条目会逐渐回收，并且交换使用量可能会在较长的一段时间内保持高于限制。这减少了对工作负载和内存管理的影响。

**memory.zswap.current 默认没有被设置**

存在于非根cgroups上的只读单值文件。

zswap压缩后端消耗的内存总量。

**memory.zswap.max 默认没有被设置**

存在于非根cgroups上的只读单值文件。

zswap压缩后端消耗的内存总量。

**memory.zswap.max 默认没有被设置**

存在于非根cgroups上的读写单值文件。默认值为“最大值”。

Zswap使用硬性限制。如果cgroup的zswap池达到此限制，它将拒绝在现有条目故障返回或写入磁盘之前获取更多存储。

**memory.pressure**

只读嵌套键控文件。

显示内存的压力失速信息。有关详细信息，请参阅官网Documentation/accounting/pis.rst

```bash
[root@server1 httpd.service]# cat memory.pressurecat: memory.pressure: Operation not supported
```

**使用指南**

“memory.high”是控制内存使用的主要机制。对高限制（高限制之和>可用内存）过度承诺，并让全局内存压力根据使用情况分配内存是一种可行的策略。

因为违反高限制不会触发OOM杀手，但会抑制有问题的cgroup，所以管理代理有足够的机会进行监控并采取适当的操作，例如授予更多内存或终止工作负载。

确定一个cgroup是否有足够的内存并不是一件小事，因为内存使用并不能表明工作负载是否可以从更多的内存中受益。例如，将从网络接收的数据写入文件的工作负载可以使用所有可用的内存，但也可以在少量内存的情况下进行性能操作。内存压力的衡量标准——工作负载由于内存不足而受到的影响有多大——是确定工作负载是否需要更多内存所必需的；不幸的是，内存压力监测机制尚未实现。

**内存所有权**

内存区域被充电到实例化它的cgroup，并保持充电到cgroup直到该区域被释放。将进程迁移到不同的cgroup并不会将它在前一个cgroup中实例化的内存使用情况移动到新的cggroup。

属于不同cgroup的进程可以使用存储器区域。该区域将被充电到哪个cgroup是确定的；然而，随着时间的推移，内存区域可能最终会出现在一个cgroup中，该cgroup具有足够的内存余量来避免高回收压力。

如果一个cgroup扫描了预计会被其他cgroup重复访问的大量内存，那么使用POSIX_FADV_ONTNEED放弃属于受影响文件的内存区域的所有权以确保正确的内存所有权可能是有意义的。

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#io)IO

“io”控制器调节io资源的分配。该控制器实现了基于权重和绝对带宽或IOPS极限分布；然而，只有在使用cfq-iosched并且两种方案都不适用于blk-mq设备的情况下，基于权重的分发才可用。

**io.stat**

只读嵌套键控文件。

行由$MAJ:$MIN设备编号键控，不排序。定义了以下嵌套键。

```bash
[root@server1 httpd.service]# cat io.stat259:0 rbytes=5042176 wbytes=4096 rios=190 wios=1 dbytes=0 dios=0253:0 rbytes=5042176 wbytes=4096 rios=190 wios=1 dbytes=0 dios=0
```

|rbytes|Bytes read|
|---|---|
|wbytes|Bytes written|
|rios|Number of read IOs|
|wios|Number of write IOs|
|dbytes|Bytes discarded|
|dios|Number of discard IOs|

**io.cost.qos 默认没有设置此参数**

一个只存在于根cgroup上的读写嵌套键控文件。

该文件配置基于IO成本模型的控制器（CONFIG_BLK_CGROUP_IOCOST）的服务质量，该控制器当前实现“IO重量”比例控制。行由$MAJ:$MIN设备编号键控，不排序。给定设备的行是在“io.cost.qos”或“io.cosst.model”上设备的第一次写入时填充的。定义了以下嵌套键。

|enable|Weight-based control enable|
|---|---|
|ctrl|“auto” or “user”|
|rpct|Read latency percentile [0, 100]|
|rlat|Read latency threshold|
|wpct|Write latency percentile [0, 100]|
|wlat|Write latency threshold|
|min|Minimum scaling percentage [1, 10000]|
|max|Maximum scaling percentage [1, 10000]|

默认情况下，控制器处于禁用状态，可以通过将“启用”设置为1来启用。“rpct”和“wpct”参数默认为零，控制器使用内部设备饱和状态将总IO速率调整在“min”和“max”之间。

当需要更好的控制质量时，可以配置延迟QoS参数。例如：

显示在sdb上，如果读取完成延迟的第95个百分位高于75ms或写入150ms，则控制器将认为设备饱和，并相应地将总IO发布率调整在50%和150%之间。

饱和点越低，以聚合带宽为代价的延迟QoS就越好。允许的“最小”和“最大”之间的调整范围越窄，IO行为就越符合成本模型。请注意，IO问题基本速率可能远未达到100%，盲目设置“最小”和“最大”可能会导致设备容量或控制质量的显著损失。“min”和“max”对于调节显示出广泛的临时行为变化的设备很有用，例如ssd，它接受以线速度写入一段时间，然后完全停滞数秒。

当“ctrl”为“auto”时，参数由内核控制，并可能自动更改。将“ctrl”设置为“user”或设置任何百分位数和延迟参数将使其进入“user”模式并禁用自动更改。通过将“ctrl”设置为“auto”，可以恢复自动模式。

**io.cost.model**

一个只存在于根cgroup上的读写嵌套键控文件。

该文件配置基于IO成本模型的控制器（CONFIG_BLK_CGROUP_IOCOST）的成本模型，该控制器当前实现“IO重量”比例控制。行由$MAJ:$MIN设备编号键控，不排序。给定设备的行是在“io.cost.qos”或“io.cosst.model”上设备的第一次写入时填充的。定义了以下嵌套键。

|ctrl|“auto” or “user”|
|---|---|
|model|The cost model in use - “linear”|

当“ctrl”为“auto”时，内核可以动态更改所有参数。当“ctrl”被设置为“user”或任何其他参数被写入时，“ctrl）”将变为“user（用户）”，并且自动更改被禁用。

当“模型”为“线性”时，将定义以下模型参数。

|[r\|w]bps|The maximum sequential IO throughput|
|---|---|
|[r\|w]seqiops|The maximum 4k sequential IOs per second|
|[r\|w]randiops|The maximum 4k random IOs per second|

根据以上内容，内置线性模型确定了顺序和随机IO的基本成本以及IO大小的成本系数。虽然很简单，但这个模型可以覆盖大多数常见的设备类别。

IO成本模型预计不会在绝对意义上准确，而是根据设备行为动态缩放。

如果需要，可以使用工具/cgroup/icost_coffe_gen.py来生成设备特定的系数。

**io.weight 此参数默认不存在**

存在于非根cgroups上的读写平面键控文件。默认值为“默认值100”。

第一行是应用于没有特定覆盖的设备的默认权重。其余的是由$MAJ:$MIN设备编号键控的覆盖，而不是排序的。权重在[110000]范围内，并指定cgroup相对于其同级可以使用的相对IO时间量。

默认重量可以通过写“默认$weight”或简单地写“$WEIGTH”来更新。可以通过写入“$MAJ:$MIN$WEIGHT”来设置覆盖，并通过写入“$MAJ:$MIN default”来取消设置覆盖。

```bash
default 1008:16 2008:0 50
```

**io.max**

存在于非根cgroups上的读写嵌套键控文件。

基于BPS和IOPS的IO限制。行由$MAJ:$MIN设备编号键控，不排序。定义了以下嵌套键。

|rbps|Max read bytes per second|
|---|---|
|wbps|Max write bytes per second|
|riops|Max read IO operations per second|
|wiops|Max write IO operations per second|

写入时，可以按任何顺序指定任意数量的嵌套键值对。可以将“max”指定为删除特定限制的值。如果多次指定同一个键，则结果是未定义的。

在每个IO方向上测量BPS和IOPS，如果达到限制，则IO会延迟。允许临时爆发。

将读取限制设置为2M BPS，将写入限制设置为120 IOPS，持续8:16：

```bash
echo "8:16 rbps=2097152 wiops=120" > io.max
```

读取会返回以下内容：

```bash
8:16 rbps=2097152 wbps=max riops=max wiops=120
```

写入IOPS限制可以通过写入以下内容来取消：

```bash
echo "8:16 wiops=max" > io.max
```

现在读取返回以下内容：

```bash
8:16 rbps=2097152 wbps=max riops=max wiops=max
```

**io.pressure**

只读嵌套键控文件。

显示IO的压力失速信息。有关详细信息，请参阅官网Documentation/accounting/pis.rst。

```bash
[root@server1 httpd.service]# cat io.pressurecat: io.pressure: Operation not supported
```

**io.latency**

这采用与其他控制器类似的格式。

“主要：次要目标=<以微秒为单位的目标时间>”

“MAJOR:MINOR target=<target time in microseconds>”

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#pid)PID

进程号控制器用于允许cgroup在达到指定限制后停止任何新任务的fork（）或clone（）。

一个cgroup中的任务数量可能会以其他控制器无法阻止的方式耗尽，从而保证其自己的控制器。例如，fork炸弹可能会在达到内存限制之前耗尽任务数量。

请注意，此控制器中使用的PID指的是内核使用的进程ID TID。

**pids.max**

存在于非根cgroups上的读写单值文件。默认值为“最大值”。

进程数量的硬性限制。

```bash
[root@server1 httpd.service]# cat pids.max24454
```

**pids.current**

存在于所有cgroup上的只读单值文件。

当前在cgroup及其子代中的进程数。

```bash
[root@server1 httpd.service]# cat pids.current213
```

**pids.events**

```bash
[root@server1 httpd.service]# cat pids.eventsmax 0
```

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#a)

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#cpuset)Cpuset

“cpuset”控制器提供了一种机制，用于将任务的CPU和内存节点位置限制为仅在任务的当前cgroup中的cpuset接口文件中指定的资源。这在大型NUMA系统上尤其有价值，在大型NUMA系统中，将作业放置在适当大小的系统子集上，并仔细放置处理器和内存，以减少跨节点内存访问和争用，可以提高整体系统性能。

“cpuset”控制器是分层的。这意味着控制器不能使用其父级中不允许使用的CPU或内存节点。

**cpuset.cpus**

一个读写多值文件，存在于启用了非根cpuset的cgroups上。

它列出了该cgroup中的任务要使用的请求CPU。然而，要授予的CPU的实际列表受到其父CPU施加的约束，并且可能与请求的CPU不同。

CPU编号是逗号分隔的数字或范围。例如：

```bash
[root@server1 httpd.service]# cat cpuset.cpus0-4,6,8-10
```

空值表示cgroup使用与最近的cgroup祖先相同的设置，具有非空的“cpuset.cpus”或所有可用的CPU（如果没有找到）。

“cpuset.cpus”的值在下一次更新之前保持不变，并且不会受到任何CPU热插拔事件的影响。

**cpuset.cpus.effective**

只读多值文件，存在于所有启用cpuset的cgroups上。

它列出了父组实际授予该cgroup的联机CPU。允许当前cgroup中的任务使用这些CPU。

如果“cpuset.cpus”为空，则“cpuset.cpus.effect”文件将显示父cgroup中可供该cgroup使用的所有CPU。否则，它应该是“cpuset.cpus”的子集，除非“cpuset.cpus”中列出的CPU都不能被授予。在这种情况下，它将被当作一个空的“cpuset.cpus”来处理。

其值将受到CPU热插拔事件的影响。

```bash
[root@server1 httpd.service]# cat cpuset.cpus.effective0-1
```

**cpuset.mems**

一个读写多值文件，存在于启用了非根cpuset的cgroups上。

它列出了此cgroup中的任务要使用的请求内存节点。然而，授予的内存节点的实际列表受到其父节点施加的约束，并且可能与请求的内存节点不同。

内存节点编号是逗号分隔的数字或范围。例如：

```bash
# cat cpuset.mems0-1,3
```

空值表示cgroup使用与最近的cgroup祖先相同的设置，具有非空的“cpuset.mems”或所有可用的内存节点（如果没有找到）。

“cpuset.mems”的值在下一次更新之前保持不变，并且不会受到任何内存节点热插拔事件的影响。

将非空值设置为“cpuset.mems”会导致cgroup内任务的内存迁移到指定节点，如果它们当前正在使用指定节点之外的内存。

这种内存迁移是有代价的。迁移可能尚未完成，并且可能会留下一些内存页。因此，建议在向cpuset中生成新任务之前，应正确设置“cpuset.mems”。即使需要用活动任务更改“cpuset.mems”，也不应该频繁进行。

**cpuset.mems.effective**

只读多值文件，存在于所有启用cpuset的cgroups上。

它列出了父组实际授予该cgroup的联机内存节点。允许当前cgroup中的任务使用这些内存节点。

如果“cpuset.mems”为空，它将显示父cgroup中可供该cgroup使用的所有内存节点。否则，它应该是“cpuset.mems”的子集，除非“cpuset.mems”中列出的任何内存节点都不能被授予。在这种情况下，它将被视为一个空的“cpuset.mems”。

其值将受到内存节点热插拔事件的影响。

```bash
[root@server1 httpd.service]# cat cpuset.mems.effective0
```

**cpuset.cpus.partition**

存在于启用了非根cpuset的cgroups上的读写单值文件。此标志归父cgroup所有，不可删除。

写入时，它只接受以下输入值。

```bash
[root@server1 httpd.service]# cat cpuset.cpus.partitionmember
```

|“member”|Non-root member of a partition|
|---|---|
|“root”|Partition root|
|“isolated”|Partition root without load balancing|

根cgroup始终是分区根，其状态无法更改。所有其他非根cgroup都以“member”开头。

当设置为“根”时，当前cgroup是一个新分区或调度域的根，该域包括它自己及其所有子体，除了那些本身是独立分区根及其子体的子体。

当设置为“隔离”时，该分区根目录中的CPU将处于隔离状态，而没有来自调度器的任何负载平衡。放置在这样一个有多个CPU的分区中的任务应该小心地分配并绑定到每个单独的CPU，以获得最佳性能。

分区根的“cpuset.cpus.effect”中显示的值是分区根可以专用于潜在的新子分区根的CPU。新的子级从其父级“cpuset.CPUs.effect”中减去可用的CPU。

分区根（“root”或“isolated”）可以处于两种可能的状态之一——有效或无效。无效的分区根处于降级状态，其中一些状态信息可能会被保留，但其行为更像是一个“成员”。

允许在“成员”、“根”和“隔离”之间进行所有可能的状态转换。

读取时，“cpuset.cpu.partition”文件可以显示以下值。

|“member”|Non-root member of a partition|
|---|---|
|“root”|Partition root|
|“isolated”|Partition root without load balancing|
|“root invalid (<reason>)”|Invalid partition root|
|“isolated invalid (<reason>)”|Invalid isolated partition root|

在分区根无效的情况下，括号中会包含一个关于分区无效原因的描述性字符串。

要使分区根目录生效，必须满足以下条件。

“cpuset.cpus”与它的兄弟姐妹是排他性的，即它们不由它的任何兄弟姐妹共享（排他性规则）。

父cgroup是有效的分区根。

“cpuset.cpus”不是空的，必须至少包含父级的“cpuset.cpus”中的一个CPU，即它们重叠。

“cpuset.cpus.effect”不能为空，除非没有与此分区关联的任务。

诸如热插拔或对“cpuset.cpus”的更改之类的外部事件可能会导致有效的分区根无效，反之亦然。请注意，不能将任务移动到“cpuset.cpus.effect”为空的cgroup中。

对于启用了同级cpu独占规则的有效分区根，对“cpuset.cpus”所做的违反独占规则的更改将使该分区及其具有冲突cpuset.cpu值的同级分区无效。因此，在更改“cpuset.cpus”时必须小心。

当没有与有效的非根父分区相关联的任务时，它可以将所有的CPU分配给它的子分区。

必须小心将有效的分区根更改为“成员”，因为它的所有子分区（如果存在）都将变得无效，从而导致在这些子分区中运行的任务中断。如果将这些未激活的分区的父分区切换回具有适当的“cpuset.cpus”集的分区根，则可以恢复这些分区。

每当“cpuset.cpu.partition”的状态发生变化时，就会触发轮询和inotify事件。这包括写入“cpuset.cpus.dartition”、cpu热插拔或其他修改分区有效性状态的更改所引起的更改。这将允许用户空间代理监视对“cpuset.cpu.partition”的意外更改，而无需进行连续轮询。

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#device-controller)Device controller

设备控制器管理对设备文件的访问。它包括创建新设备文件（使用mknod）和访问现有设备文件。

Cgroup v2设备控制器没有接口文件，并且是在Cgroup BPF之上实现的。为了控制对设备文件的访问，用户可以创建类型为bpf_PROG_type_CGROUP_device的bpf程序，并将它们附加到带有bpf_CGROUP-device标志的CGROUP。在尝试访问设备文件时，将执行相应的BPF程序，根据返回值，使用-EPERM尝试将成功或失败。

BPF_PROG_TYPE_CGROUP_DEVICE程序将指针指向BPF_CGROUP_dev_ctx结构，该结构描述设备访问尝试：访问类型（mknod/read/write）和设备（类型、主要数字和次要数字）。如果程序返回0，则使用-EPERM尝试失败，否则尝试成功。

BPF_PROG_TYPE_CGROUP_DEVICE程序的一个示例可以在内核源代码树中的tools/testing/selftests/BPF/progs/dev_CGROUP.c中找到。

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#rdma)RDMA

“rdma”控制器负责管理rdma资源的分配和核算。

**rdma.max**

一种读写嵌套键控文件，存在于除root以外的所有cgroup，用于描述RDMA/IB设备的当前配置资源限制。

行由设备名称键入，并且不按顺序排列。每一行都包含以空格分隔的资源名称及其可分配的配置限制。

定义了以下嵌套键。

|hca_handle|Maximum number of HCA Handles|
|---|---|
|hca_object|Maximum number of HCA Objects|

mlx4和ocrdma设备的示例如下：

```bash
mlx4_0 hca_handle=2 hca_object=2000ocrdma1 hca_handle=3 hca_object=max
```

**rdma.current**

描述当前资源使用情况的只读文件。它存在于除根以外的所有cgroup。

mlx4和ocrdma设备的示例如下：

```bash
mlx4_0 hca_handle=1 hca_object=20ocrdma1 hca_handle=1 hca_object=23
```

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#hugetlb)HugeTLB

HugeTLB控制器允许限制每个控制组的HugeTLB使用，并在页面故障期间强制执行控制器限制。

hugetlb.<hugepagesize>.current :

显示“hugepadgesize”hugetlb的当前用法。它存在于除根以外的所有cgroup。

hugetlb.<hugepagesize>.max

设置/显示“hugepagesize”hugetlb用法的硬限制。默认值为“max”。它存在于除根以外的所有cgroup。

hugetlb.<hugepagesize>.events

存在于非根cgroups上的只读平面键控文件。

max : 由于HugeTLB限制而导致的分配失败次数

hugetlb.<hugepagesize>.events.local

类似于hugetlb<hugepageize>.events，但文件中的字段是cgroup的本地字段，即不具有层次结构。在此文件上生成的文件修改事件仅反映本地事件。

hugetlb.<hugepagesize>.numa_stat

与memory.numa_stat类似，它显示了该cgroup中<hugepagesize>的hugetlb页面的numa信息。只包括使用中的活动hugetlb页面。每个节点的值以字节为单位。

### [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#misc)Misc

Miscellaneous cgroup为标量资源提供了资源限制和跟踪机制，标量资源不能像其他cgroup资源那样抽象。控制器由CONFIG_CGROUP_MISC配置选项启用。

可以通过include/linux/misc_group.h文件中的enum misc_res_type｛｝向控制器添加资源，并通过kernel/cgroup/misc.c文件中的misc_res_name[]向控制器添加相应的名称。在使用资源之前，资源的提供程序必须通过调用misc_cg_set_capacity（）来设置其容量。

一旦设置了容量，就可以使用收费和不收费API来更新资源使用情况。所有与misc控制器交互的API都在include/linux/misc_group.h中。

**misc.capacity**

仅在根cgroup中显示的只读平面键控文件。它显示了平台上可用的各种标量资源及其数量：

```bash
$ cat misc.capacityres_a 50res_b 10
```

**misc.current**

显示在非根cgroups中的只读平面键控文件。它显示了cgroup及其子组中资源的当前使用情况

```bash
$ cat misc.currentres_a 3res_b 0
```

**misc.max**

非根cgroups中显示的读写平面键控文件。允许最大限度地使用cgroup及其子组中的资源。：

```bash
$ cat misc.maxres_a maxres_b 4
```

可以通过以下方式设置限制：

```bash
# echo res_a 1 > misc.max
```

可以通过以下方式将限制设置为最大值：

```bash
# echo res_a max > misc.max
```

可以将限制设置为高于misc.capacity文件中的容量值。

**misc.events**

存在于非根cgroups上的只读平面键控文件。定义了以下条目。除非另有规定，否则此文件中的值更改将生成文件修改事件。此文件中的所有字段都是分层的。

max: cgroup的资源使用率即将超过最大边界的次数。

## [](https://note.youdao.com/md/preview.html?file=%2Fyws%2Fapi%2Fpersonal%2Ffile%2FWEB9ca4beb687107b1e935ddeb0c4e48567%3Fmethod%3Ddownload%26read%3Dtrue%26shareKey%3Dd94e7b196d9677a39cc0ddaff271fa3f#%E4%B8%BAsystemd%E5%90%AF%E5%8A%A8%E7%9A%84%E6%9C%8D%E5%8A%A1%E6%B7%BB%E5%8A%A0cgroup%E9%99%90%E5%88%B6)为systemd启动的服务添加cgroup限制

查看有哪些cgroup配置项可用:

```bash
[root@server1 httpd.service]# man systemd.resource-control
```

这里可以使用命令，也可以直接使用echo进行修改。

```bash
[root@server1 httpd.service]# systemctl set-property httpd.service MemoryLimit=512M[root@server1 httpd.service]# lscgroup.controllers      cpuset.cpus.effective  memory.lowcgroup.events           cpuset.cpus.partition  memory.maxcgroup.freeze           cpuset.mems            memory.mincgroup.kill             cpuset.mems.effective  memory.numa_statcgroup.max.depth        cpu.stat               memory.oom.groupcgroup.max.descendants  cpu.weight             memory.pressurecgroup.procs            cpu.weight.nice        memory.statcgroup.stat             io.bfq.weight          memory.swap.currentcgroup.subtree_control  io.latency             memory.swap.eventscgroup.threads          io.max                 memory.swap.highcgroup.type             io.pressure            memory.swap.maxcpu.idle                io.stat                pids.currentcpu.max                 memory.current         pids.eventscpu.max.burst           memory.events          pids.maxcpu.pressure            memory.events.localcpuset.cpus             memory.high[root@server1 httpd.service]# cat memory.max 536870912
```

注意:即使服务重启,这个cgroup限制仍然会起作用，

因为systemctl已经把它写到了service文件中，

```bash
[root@server1 httpd.service.d]# systemctl cat nginxNo files found for nginx.service.[root@server1 httpd.service.d]# systemctl cat httpd.service # /usr/lib/systemd/system/httpd.service# See httpd.service(8) for more information on using the httpd service.# Modifying this file in-place is not recommended, because changes# will be overwritten during package upgrades.  To customize the# behaviour, run "systemctl edit httpd" to create an override unit.# For example, to pass additional options (such as -D definitions) to# the httpd binary at startup, create an override unit (as is done by# systemctl edit) and enter the following:#       [Service]#       Environment=OPTIONS=-DMY_DEFINE[Unit]Description=The Apache HTTP ServerWants=httpd-init.serviceAfter=network.target remote-fs.target nss-lookup.target httpd-init.serviceDocumentation=man:httpd.service(8)[Service]Type=notifyEnvironment=LANG=CExecStart=/usr/sbin/httpd $OPTIONS -DFOREGROUNDExecReload=/usr/sbin/httpd $OPTIONS -k graceful# Send SIGWINCH for graceful stopKillSignal=SIGWINCHKillMode=mixedPrivateTmp=trueOOMPolicy=continue[Install]WantedBy=multi-user.target# /etc/systemd/system.control/httpd.service.d/50-MemoryLimit.conf# This is a drop-in unit file extension, created via "systemctl set-property"# or an equivalent operation. Do not edit.[Service]MemoryLimit=536870912
```

看到最下面提示的内容，和文件路径，我们也可以查看。

```bash
[root@server1 httpd.service]# cat /etc/systemd/system.control/httpd.service.d/50-MemoryLimit.conf# This is a drop-in unit file extension, created via "systemctl set-property"# or an equivalent operation. Do not edit.[Service]MemoryLimit=536870912[root@server1 httpd.service]# cd /etc/systemd/system.control/httpd.service.d/[root@server1 httpd.service.d]# ls50-MemoryLimit.conf
```

其他常用命令：

设置cpu使用率最高不超过单颗cpu的80%

```bash
systemctl set-property httpd.service CPUQuota=80%
```