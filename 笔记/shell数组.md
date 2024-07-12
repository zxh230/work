#### shell数组

1. 如何创建数组，以数组arry示例

   ```shell
   # 第一种方法
   arry=$(echo {a..z} {A..Z} {0..9} _)
   # 第二种方法
   arry=(aaa bbb ccc)
   # 第三种方法
   arry[0]=bbb
   arry[5]=fff
   # 查询数组
   echo ${arry[0]} # 查询arry数组中第一个位置的值
   echo ${arry[*]} # 查询arry数组中所有的值
   ```

   