要求：
写 yaml 文件 deployment 部署 nginx 副本 3 个.
写 yaml 文件 statefulset 部署 php 副本 3 个.
写 yaml 文件 statefulset 部署 mysql 副本 1 个.
写 yaml 文件以上每个部署一个 service.
写 yaml 文件 ingress 代理 https 协议的证书和密钥.
写 yaml 文件将证书和密钥作为 secret 存储
写 yaml 文件创建 nginx 的相关配置文件, php 的相关配置文件, mysql 的相关配置文件, 作为 configmap.
要求: 
1 将上述文件作为 helm 文件.
2 在 node 2 构建 helm 的私有 repository 仓库.
3 使用私有仓库文件内的 repo 安装以上全部文件.
结果:
访问 https://www.han.com/ 可以看到内容为: php 的测试页面及 mysql 连接测试.
>实验步骤

```shell

```