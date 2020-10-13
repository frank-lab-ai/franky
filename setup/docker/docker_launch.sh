echo "## stopping and removing frank-api container ..."
docker stop frank-api
docker rm frank-api

#echo "## undo all local changes in local repo"
cd /data/frank/api
#git reset --hard

#echo "## pull changes from git"  
#git pull

echo "## creating logs directory if they do not exist"
mkdir -p /data/frank/api/logs/uwsgi 
mkdir -p /data/frank/api/logs/nginx

echo "## recreating frank-api container ..."
docker run -d --name frank-api \
  -v /data/frank/api/config.py:/app/config.py \
  -v /data/frank/api/logs/nginx:/var/log/nginx  \
  -v /data/frank/api/logs/uwsgi:/app/logs/uwsgi  \
  --net franknet0 \
  --ip 172.20.0.3 \
  --restart always nkobby/frank-server:1.0

echo "## Done! Status of frank-api container: "
docker inspect --format="{{json .State}}" frank-api