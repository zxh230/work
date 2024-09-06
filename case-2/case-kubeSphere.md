安装 nfs
```shell
yum -y install nfs-utils
cat << EOF | tee /etc/exports
/nfs *(sync,no_root_squech)
EOF
systemctl start nfs-server.service
```