docker-compose 通过使用一个 yml/yaml 配置文件完成
docker-compose 将所管理的容器分为三层
	工程/project：理解成一个目录，这个目录下有唯一的 docker-compose. yml 文件，extends 文件和变量文件等等
	注意，如果没有指定 project name 就把当前目录的名字作为 project name

