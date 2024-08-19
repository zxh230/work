修改 daemon. json 文件

```shell
vim /etc/docker/daemon.json
###
{
"registry-mirrors": [
        "https://docker.1panel.live.=",
        "https://docker.m.daoclude.io",
        "https://6kskcyjq.mirror.aliyuncs.com"
],
 "experimental" : true
}
###
# 重启
systemctl daemon-reload 
systemctl restart docker
```

docker 的检查点
checkpoint  针对进程，无法恢复删除的数据
1. 在不停止/容器的情况下启动主机
2. 加快慢速启动应用程序的启动时间
3. 将"倒带"进程还原到比较早的时间点
4. 正在运行的进程进行"取证调试"（错误的反复）