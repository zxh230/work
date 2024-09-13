
```shell
# 安装依赖
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo yum -y install terraform
# 部署两台ECS
mkdir ecs
cd ecs
vim ecs.tf
###
provider "alicloud" {
  region      = "cn-beijing"
  access_key  = "填写自己的用户AccessKey ID"
  secret_key  = "填写自己的AccessKey Secret"
}

resource "alicloud_instance" "ecs_instance" {
  count                      = 2
  instance_type              = "ecs.hfg6.large"
  security_groups            = ["sg-2ze7vq5ytym21iiivy1a"]
  vswitch_id                 = "vsw-2zejrm9x3ri5hcqzveroy"
  image_id                   = "rockylinux_9_4_x64_20G_alibase_20240709.vhd"
  system_disk_category       = "cloud_efficiency"
  system_disk_size           = 40
  internet_charge_type       = "PayByTraffic"
  internet_max_bandwidth_out = 5
  instance_charge_type       = "PostPaid"
  instance_name              = "nginx-bj-11"
  password                   = "123.comAA"
  host_name                  = "server${count.index + 2}"
}
output "instance_ids" {
  value = alicloud_instance.ecs_instance.*.id
}
output "instance_ips" {
  value = alicloud_instance.ecs_instance.*.public_ip
}
###
```

授权

[RAM 访问控制 (aliyun.com)](https://ram.console.aliyun.com/users)

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903180114.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903180156.png)

```shell
# 部署之前确认自己的阿里云账户余额超过100元
# 部署
terraform init
terraform apply
```

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903180252.png)
![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903180301.png)

创建完成

前往阿里云查看

[云服务器管理控制台 (aliyun.com)](https://ecs.console.aliyun.com/home)

新创建的 ecs

![image.png](https://gitee.com/zhaojiedong/img/raw/master/20240903180342.png)

