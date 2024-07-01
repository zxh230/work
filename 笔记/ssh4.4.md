生成一对密钥文件

ssh-keygen

发送公钥文件

ssh-copy-id -i /root/.ssh/id_rsa node02

将私钥转换为公钥

ssh-keygen -y -f /root/.ssh/id_rsa

是否允许root登录，修改为no禁止root登录

grep -n ^Permit /etc/ssh/sshd_config