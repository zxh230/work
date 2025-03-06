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

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20250306171738.png)

