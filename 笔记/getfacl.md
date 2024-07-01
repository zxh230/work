---
typora-copy-images-to: upload
---

![image-20240520085440900](https://gitee.com/zhaojiedong/img/raw/master/202405200855597.png)

getfacl /var/run/php-fpm/www.sock

查看文件访问控制列表

```shell
setfacl -m u:zhaojiedong:rw- /var/run/php-fpm/www.sock 
```

设置文件访问控制列表