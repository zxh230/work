安装 Helm

[下载Heml](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/helm-v3.15.3-linux-amd64.tar.gz)
```shell
# 配置heml命令包
tar -xf helm-v3.15.3-linux-amd64.tar.gz
cd linux-amd64
chmod +x heml
mv heml /usr/local/sbin/
# 使其可以tab
echo "source <(helm completion bash)" >> ~/.bashrc
source ~/.bashrc
# 添加仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
# 查看helm仓库
helm repo list
# 查找仓库中含有的软件，例：mysql
helm search repo bitnami |grep mysql
# 更新软件包
helm repo update
# helm安装mysql
helm install bitnami/mysql --generate-name
# 查看已安装列表
helm list 
# 卸载
helm uninstall <软件包名>
```
安装

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061022913.png)

卸载

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061021329.png)



helm 的三大概念：

chart：代表 helm 的包，可以看作：dnf，apt，brew，

repostory：用来存放和共享 charts 的地方，可以看作为：仓库地址

release：是 kubernetes 中 chart 的实例

helm 安装 charts 到 kubernetes 中，每次安装都会创建一个新的 release，可以在 helm 的 chart repository 中寻找到新的 chart

helm 安装 pod 的两种方法

```shell
# 使用tar包部署
helm pull bitnami/zookeeper
# 解压
tar -xf zookeeper-13.4.10.tgz
cd zookeeper/
# 修改values.yaml
vim values.yaml +700
###修改
enabled: false
replicaCount: 3
registry: docker.io
###
# 安装，.应为values.yaml文件所在位置
helm install zookeeper .
# 当需要删除时
helm uninstall zookeeper .
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061108646.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061109077.png)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061110505.png)

验证
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061119091.png)
******

```shell
# 命令直接部署
helm install kafka bitnami/kafka --version 26.11.4 --set zookeeper.enabled=false --set controller.replicaCount=3 --set controller.persistence.enabled=false --set clusterDomain=hansir.good
# 验证
kubectl get po
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061118399.png)

```shell
# 查看设置的变量
helm get values kafka 
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061118408.png)

******

helm 安装的 pod 可以进行扩缩等操作

```shell
kubectl scale statefulset kafka-controller --replicas 5
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061120847.png)

创建一个新的 helm Chart
```shell
helm create helm-test
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061127021.png)

安装 helmify
[helmify安装](https://gitee.com/zhaojiedong/work/raw/master/%E6%96%87%E4%BB%B6/helmify_Linux_x86_64.tar.gz)

```shell
# 解压
tar -xf helmify_Linux_x86_64.tar.gz
mv helmify /usr/local/sbin/
# 验证
helmify -version
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408061138744.png)

helmify
chart. yaml：包含 chart 的信息，例如名字，版本，描述等
templates：包含安装 helm chart 时最终部署的所有清单文件
valumes：定义模板中的值，例如 replicas image 等等

tips：
1 helmify 不会覆盖文件，官方故意这么做的（每次修改都需要删除重新装）
2 helmify 不会删除现有模板文件，只会覆盖（一个目录下只有一个模板）
3 helmify 的所有变更都从下一次部署开始
4 注意 labels 标签，如果之前用了，最好重头删除再重新生成


helmify 自定义安装

```shell
# 将之前的nginx.yaml用helmify转写
cat nginx.yaml|  helmify nginx-zxh
# 安装
helm install nginx-zxh --generate-name 
# 打包
helm package nginx-zxh
# 使用tar包安装
helm install web-zxh nginx-zxh-0.1.0.tgz 
```

部署私人的 repo 服务器

kube 01:
```shell
scp /usr/local/sbin/helm kube02:/usr/local/sbin/helm
scp /usr/local/sbin/helmify kube02:/usr/local/sbin/helmify
```
kube 02:

```shell
# 安装并启动httpd
yum -yq install httpd
systemctl start httpd
```