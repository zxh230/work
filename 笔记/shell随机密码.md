#### shell随机密码

```shell
#!/bin/bash

letters=$(echo {a..z} {A..Z} {0..9} _)
array=($letters)
for i in $(seq 1 10)
do
  c=${array[$[$RANDOM%63]]}
  passwd[$i]=$c
done
#echo ${passwd[*]} | sed 's/ //g' # 消除数组输出后的空格
#echo ${passwd[*]} | tr -d ' '    # 消除数组输出后的空格
user_pass=$(echo ${passwd[*]} | tr -d ' ')
echo "用户密码：$user_pass"
```

运行时输出结果为

![image-20240703095428245](https://gitee.com/zhaojiedong/img/raw/master/image-20240703095428245.png)