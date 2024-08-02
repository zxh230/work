要求：
service的端口号为：9090。
使用ingress金丝雀发布：当“头部消息”有vip:user，显示：[name]。否则显示“hansir”
使用ingress实现：1、访问域名[name].com，跳转到https://www.[name].com
2、访问域名https://www.[name].com/canary/new：显示：hansir
3、访问域名https://www.[name].com/stable/old：显示：[name]
其中，[name] 将替换为 `zxh` ,如有需要可自行替换

> 开始编写

```shell
# 编写new.yaml
vim new.yaml
###

###
```