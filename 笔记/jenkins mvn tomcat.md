### jenkins+mvn+tomcat发布任务

jenkins.example.cn:配置war包

git.example.cn:中转git仓库

node04.example.cn:tomcat网站

1. 在node04上安装tomcat，解压[tomcat.tgz](https://gitee.com/zhaojiedong/img/raw/master/%E6%96%87%E4%BB%B6/apache-tomcat-10.1.13.tar.gz)(点击下载)

   ```shell
   yum -yq install java-11-openjdk
   tar -xf apache-tomcat-10.1.13.tar.gz
   mv apache-tomcat-10.1.13 /usr/local/tomcat/
   # 修改配置文件
   vim /usr/local/tomcat/conf/tomcat-users.xml +21
   # 添加
   <role rolename="admin-gui"/>
   <role rolename="manager-gui"/>
   <role rolename="manager-script"/>
   <user username="admin" password="admin" roles="admin-gui,manager-gui,manager-script"/>
   ```

   ![image-20240617094525741](https://gitee.com/zhaojiedong/img/raw/master/202406180852780.png)

   ```shell
   sed -i 's/127/10/g' /usr/local/tomcat/webapps/{docs,examples,host-manager,manager}/META-INF/context.xml
   # 启动tomcat
   /usr/local/tomcat/bin/startup.sh
   ```

   访问tomcat

   10.15.200.104:8080（用户名密码默认为admin）

2. 在jenkins上mvn打包

   ```shell
   # 将helloworld.git打包
   cd /tmp/
   rm -rf *
   git clone git@git.example.cn:/home/git/repos/helloworld.git
   cd helloworld/
   mvn clean install -D maven.test.skip=true
   # 启动jenkins
   java -jar jenkins_2.426.2.war
   ```

   打开Jenkins网页

   http://jenkins.example.cn:8080/

3. 新建任务

   任务名为：mvn-helloworld

   风格为：构建一个maven项目

4. 任务配置

   描述：java mvn to tomcat

   源码管理选择git

   配置git仓库URL

   ![image-20240617095619938](https://gitee.com/zhaojiedong/img/raw/master/202406170956964.png)

   Build配置：

   Goals and options：

   clean install -D maven.test.skip=true

![image-20240617095805005](https://gitee.com/zhaojiedong/img/raw/master/202406170958029.png)

构建后操作选择**Deploy war/ear to a container**

![image-20240617100309590](https://gitee.com/zhaojiedong/img/raw/master/202406171003625.png)

保存任务，运行后访问10.15.200.104:8080/hello/

![image-20240617100559548](https://gitee.com/zhaojiedong/img/raw/master/202406180852022.png)