docker run --name=mysql -v /var/lib/docker/volumes/8c8138c882f64beb429b74c3d937ea8b920401035934bafec9df68845eebc00f/_data:/var/lib/mysql:rw -e MYSQL_ROOT_PASSWORD=daniel1995 -p 3306:3306 -d mysql

docker exec -it mysql bash
mysql -uroot -p
create database twitter;
