```shell
# 新建一个configmaps
kubectl create configmap tomcat-config --from-literal tomcat_port=8080 --from-literal server_name=my.tomcat.com
# 查看
kubectl get configmaps
# 查看详细信息
kubectl describe configmaps tomcat-config
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021003846.png)

```shell
# 输出为yaml文件格式
kubectl get configmaps tomcat-config -o yaml
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021004552.png)

```shell

```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021008482.png)
```shell
kubectl create configmap dir --from-file /root/configmap/
kubectl describe configmaps dir 
```
![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021009564.png)

创建一个配置文件

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021010111.png)

部署

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021010654.png)

改变configmap时，之前的配置不会发生变化

![image.png](https://gitee.com/zhaojiedong/img/raw/master/202408021011924.png)

