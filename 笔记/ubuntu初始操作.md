==**实例系统版本：ubuntu 24.10-server 最小化版本**==
#### 最小化默认不自带任何文本编译器，需要自行下载
 在不新增任何文本编辑器之前，可以使用 `cat>> <<` 与 `sed -i` 对文件进行覆盖写入, 但十分麻烦
 
安装软件包之前可以更新 apt 源
```shell
sudo apt update
apt-get install -y vim # 直接安装vim
```

安装之后允许 root 进行 ssh 远程登录
```shell
vim /etc/ssh/sshd_config # 修改sshd配置文件
```

取消此行注释并修改为 yes

a
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20250306171738.png)

修改完成后重启 sshd 服务

```shell
service ssh restart
```
##### 关闭登录时系统弹出的消息提醒

在每次 ssh 登录时，系统会弹出消息：

```shell
Welcome to Ubuntu 24.10 (GNU/Linux 6.11.0-19-generic x86_64) 
	
	* Documentation: https://help.ubuntu.com 
	* Management: https://landscape.canonical.com 
	* Support: https://ubuntu.com/pro 

This system has been minimized by removing packages and content that are not required on a system that users do not log into.

To restorethis content, you can run the 'unminimize' command.
```

该消息是Ubuntu 最小化安装后的默认提示信息，目的是提醒用户系统已经过精简，移除了不必要的软件包和内容

禁用 MOTD（Message of the Day）使其不再提醒

```shell
vim /etc/pam.d/sshd
# 找到以下行
session    optional     pam_motd.so  motd=/run/motd.dynamic
session    optional     pam_motd.so noupdate
# 行首添加#将其注释掉
# 保存退出后重启ssh服务
service ssh restart
```

也可以自定义 MOTD 消息的内容

```shell
vim /etc/motd
###
可以输入自定义内容
###
# 重启sshd服务
service ssh restart
```

##### 关闭安全模块

```shell
systemctl disable apparmor
```

