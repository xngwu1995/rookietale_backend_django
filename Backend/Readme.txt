docker build -t django .
docker container run -t -d --name django -v `pwd`/Django:/app -p 8080:8000 django8000
docker exec -it django bash
