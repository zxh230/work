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

查看参数

```shell
docker run --help |grep security
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240819162730.png)


==--security-opt== 允许你设置额外的安全选项

seccomp=unconfined：意味着容器将运行在不受限的安全环境中，通常意味着容器可以执行任何系统级别的特权操作

```shell
docker run --security-opt seccomp:unconfined --name cr -d busybox:1.36 /bin/sh -c 'i=0; while true; do echo $i; i=$(expr $i + 1); sleep 1; done'
```

