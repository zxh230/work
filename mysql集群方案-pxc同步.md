系统环境：
系统为 pxc 批量装机的系统，网段为 10.15.200.0/24
网关：10.15.200.254
node 01：10.15.200.101
node 02：10.15.200.102
node 03：10.15.200.103
均已关闭防火墙与 selinux

#### 1. 安装 Percona-XtraDB-Cluster-57
```bash
# 安装yum库
for h in {1..3}
do
ssh node0$h "yum -y install https://repo.percona.com/yum/percona-release-latest.noarch.rpm"
done
# 启用

```