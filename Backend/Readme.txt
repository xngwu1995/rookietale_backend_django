docker build -t django .
docker container run -t -d --name django -v `pwd`/Django:/app -p 8080:80 django
docker exec -it django bash
