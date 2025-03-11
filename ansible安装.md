导入 [ansible软件包](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/ansible.el9.tgz)

解压并配置 yum 库

```bash
tar -xf ansible.el9.tgz
# 配置yum仓库
vim /etc/yum.repos.d/ansible.repo
###
[BaaseOS]
name=BaaseOS
baseurl=file:///root/ansible
gpgcheck=0
enabled=1
###
# 清理yum缓存
yum makecache
# 安装
yum -y install ansible
# 修改配置文件
vim /etc/ansible/ansible.cfg
###
[defaults]
inventory = /etc/ansible/inventory 
remote_user = root 
host_key_checking = False
###
# 配置清单

```