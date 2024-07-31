下载部署文件
[deploy.yaml](https://gitee.com/zhaojiedong/work/blob/master/%E6%96%87%E4%BB%B6/deploy.yaml)
修改部署文件
==修改文件中第449，550，603行的镜像地址为自己阿里云私人仓库的地址==
![](https://gitee.com/zhaojiedong/img/raw/master/202407311447118.png)

 ![](https://gitee.com/zhaojiedong/img/raw/master/202407311447744.png)

 ![](https://gitee.com/zhaojiedong/img/raw/master/202407311447963.png)
>vim编辑器用法：
>D 删除当前行内光标后的内容
>: noh  取消搜索高亮
>搜索后 n 查找下一个
##### 下载镜像
```shell
# kube01
nerdctl --namespace k8s.io pull registry.cn-hangzhou.aliyuncs.com/zxh230/controller:v1.10.1
nerdctl --namespace k8s.io pull registry.cn-hangzhou.aliyuncs.com/zxh230/kube-webhook-certgen:v1.4.1
# kube02
nerdctl --namespace k8s.io pull registry.cn-hangzhou.aliyuncs.com/zxh230/kube-webhook-certgen:v1.4.1
# kube03
nerdctl --namespace k8s.io pull registry.cn-hangzhou.aliyuncs.com/zxh230/kube-webhook-certgen:v1.4.1
```
##### 修改deploy.yaml文件
```shell
vim deploy.yaml +423
# 添加
hostNetwork: true
nodeName: kube01
# 注：主机名为下载了 controller:v1.10.1 镜像的主机
```
![](https://gitee.com/zhaojiedong/img/raw/master/202407311503183.png)
##### 验证*
```shell
# 验证kube01镜像是否安装
nerdctl images --namespace k8s.io |grep -E "controller|webhook"
# 验证kube02镜像是否安装
nerdctl images --namespace k8s.io |grep -E "webhook"
# 验证kube03镜像是否安装
nerdctl images --namespace k8s.io |grep -E "webhook"
# 查看文件中镜像是否与安装镜像名一致，主机配置是否正确，此命令无需更改
cat deploy.yaml |grep -E "hostNetwork|nodeName|image: registry.cn-hangzhou.aliyuncs.com"
```
kube01
![](https://gitee.com/zhaojiedong/img/raw/master/202407311519178.png)
kube02
![](https://gitee.com/zhaojiedong/img/raw/master/202407311520031.png)
kube03
![](https://gitee.com/zhaojiedong/img/raw/master/202407311521183.png)
配置文件
![](https://gitee.com/zhaojiedong/img/raw/master/202407311521079.png)
==注意主机名是否正确==
##### 修改完成后开始部署
```shell
kubectl apply -f deploy.yaml
```
![](https://gitee.com/zhaojiedong/img/raw/master/202407311505895.png '部署完成')
验证：
```shell
# 稍稍等待
kubectl get pods -n ingress-nginx
```
![](https://gitee.com/zhaojiedong/img/raw/master/202407311524756.png)
安装完成，Completed为容器已完成状态，没有报错