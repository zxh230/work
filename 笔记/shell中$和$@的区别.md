# shell中$*和\$@的区别

1. 新建一个shell脚本文件

   ```shell
   #!/bin/bash
   echo '$*= '$*
   for i in "$*"
   do
   echo $i
   done
   echo 'xxxxxxxxx'
   echo '$@= '$@
   for j in "$@"
   do
   echo $j
   done
   ```

2. 运行该脚本时添加参数a b c d(使用空格隔开)

   ![image-20240703084521244](https://gitee.com/zhaojiedong/img/raw/master/image-20240703084521244.png)

   ==可以看到，当使用for循环时，$*将所有输入参数作为一个整体，\$@则是将传入参数分割==