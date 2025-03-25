docker-compose 通过使用一个 yml/yaml 配置文件完成
docker-compose 将所管理的容器分为三层
	工程/project：理解成一个目录，这个目录下有唯一的 docker-compose. yml 文件，extends 文件和变量文件等等
	注意，如果没有指定 project name 就把当前目录的名字作为 project name


```shell
# docker-compose示例
vim docker-compose.yaml
###
services: 
  db:
    container_name: mysql
    image: mysql:8
    restart: always
    volumes:
    - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: wordpress
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress

  wordpress:
    depends_on:
    - db
    container_name: web
    image: wordpress:latest
    links:
    - db
    volumes:
    - wp_site:/var/www/html
    ports:
    - 443:443
    - 80:80
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
volumes:
  db_data:
  wp_site:
###
```

