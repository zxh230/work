ansible 配置文件实例：

> [defaults]
> inventory = /etc/ansible/inventory
> remote_user = root
> host_key_checking = False

编写清单
vim /etc/ansible/inventory 

变量类型：
node01  ansible_ssh_user=root ansible_ssh_pass=123.com ## 主机变量

[blog:vars]  ## 组变量

ansible_ssh_user=root
ansible_ssh_pass=123.com

[all:vars]  ## 全局变量

ansible_ssh_user=root
ansible_ssh_pass=123.com

优先级主机>组>全局



ansible all -m ping

ansible-inventory --graph

ansible-inventory --list

ansible为blog组安装httpd，php，php-mysqlnd

ansible blog -m shell -a 'yum -y install httpd php php-mysqlnd'

-m：调用模块

报错实例：

node01 | UNREACHABLE! => {
    "changed": false,
    "msg": "Invalid/incorrect password: Warning: Permanently added 'node01' (ED25519) to the list of known hosts.\r\nPermission denied, please try again.",
    "unreachable": true
} ## 用户名和密码不匹配

10.15.200.103 | UNREACHABLE! => {
    "changed": false,
    "msg": "Failed to connect to the host via ssh: ssh: connect to host 10.15.200.103 port 22: No route to host",
    "unreachable": true
} ## 未开机



yum安装包

​    name：httpd

​	state：present    出席 （ubuntu  centos）

​	state：absent     离席    remove

yum_repository配置仓库

copy复制文件（管理端--->被管理端）

file目录链接（被管理端）

service：systemctl XXX unit

​		name：httpd

​		state：started

template模板





ansible blog -m yum -a 'name=httpd state=present'  



ansible-doc yum | grep -A100 EX  ## 帮助

ansible blog -m shell -a 'systemctl is-active httpd;systemctl is-enabled httpd' 

查看是否启动并设置开机自启

yaml：（yml）  jinja2  ### 空格tab不能混用，要求缩进

\- name: install php   ##描述信息

  yum:

​		name: httpd

​		state: present

每个  :   后必须有空格（除了行尾）

每个 -  后面必须有空格

echo "autocmd FileType yaml setlocal ai ts=2 sw=2 et" > $HOME/.vimrc 

\### 自动补全 将一个 tab 设置为 默认两个 空格

blog.yml

![image-20240408113058378](https://gitee.com/zhaojiedong/img/raw/master/202404141758973.png)

ansible-playbook --syntax-check blog.yml  ## 检查语法

ansible-playbook blog.yml ## 运行yml剧本





![image-20240409084552081](https://gitee.com/zhaojiedong/img/raw/master/202404141758974.png)![image-20240409084742771](https://gitee.com/zhaojiedong/img/raw/master/202404141758975.png)

遍历列表变量，item（s）复数形式



![image-20240409084908800](https://gitee.com/zhaojiedong/img/raw/master/202404141758977.png)

也可以用loop控制变量item

replace模块：替换文件内文本内容

path：路径

regexp：源文本

replace：替换文本

unarchive：解包模块

src：包路径

dest：目标路径

remote_src: yes使用远端

<img src="https://gitee.com/zhaojiedong/img/raw/master/202404141758042.png" alt="image-20240409095436919"  />

mariadb数据库剧本

 [zhaojiedong.yml](D:\zhaojiedong.yml) 

安装wordpress（node03,node04）

安装mariadb（node01）

安装nfs（node02）





ansible node01 -m setup  ##显示node01所有信息

![image-20240410084520457](https://gitee.com/zhaojiedong/img/raw/master/202404141758978.png)网络信息



获取ip与主机名（hosts.j2）：

<img src="https://gitee.com/zhaojiedong/img/raw/master/202404141758979.png" alt="image-20240410095940961" style="zoom: 200%;" />

{% for h in groups['all']%}

{{hostvars[h]\['ansible_default_ipv4']['address']}} {{hostvars[h]\['ansible_fqdn']}} {{hostvars[h]\['ansible_hostname']}}

{%endfor%}



![image-20240411093749478](https://gitee.com/zhaojiedong/img/raw/master/202404141758980.png)自定义变量pack



![image-20240411095025920](https://gitee.com/zhaojiedong/img/raw/master/202404141758981.png)

事件通知notify

触发器handlers

*用来触发任务*

![image-20240411101603423](https://gitee.com/zhaojiedong/img/raw/master/202404141758982.png)

![image-20240411101534604](https://gitee.com/zhaojiedong/img/raw/master/202404141758983.png)

模板中的自定义变量需要在清单中进行定义

ansible-galaxy init apache  ## 初始化角色

编辑顺序：

角色目录中应有files（文件目录）,handlers（触发器目录）,tasks（任务目录）,templates（模板目录）,vars（变量目录）几个基本目录

![image-20240412134733844](https://gitee.com/zhaojiedong/img/raw/master/202404141758984.png)

1.tasks：main.yml任务清单--（- include_tasks: XXXX.yml）-XXXX.yml具体任务

2.任务中是否使用template模板文件

​	在template目录中创建该模板

3.任务中是否使用到静态文件

​	将文件移动到files目录

4.模板中是否有自定义变量，该变量的值是否固定	

​	固定变量：写入vars/main.yml文件（“变量名”："变量值"）
​		*mode: MASTER
​	不固定变量：在清单中写入主机后（"变量名"=“变量值”）
​		*10.15.200.101 mode=MASTER*
​		*10.15.200.102 mode=BACKUP
5.任务中是否有触发器

​	在handlers/main.yml中写入触发器名

​		例：- name: restart_httpd
​			 service: 
​				name: httpd
​				state: restarted
6.
