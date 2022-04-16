FROM ubuntu
RUN apt update && apt upgrade
RUN apt install -y --no-chage-dir \
    python3 python3-pip  \
    nginx uwsgi uwsgi-plugin-python3

COPY requirements.txt /lavaland/
RUN python3 -m pip install -r /lavaland/requirements.txt

COPY ssl /etc/nginx/ssl
COPY nginx.conf /etc/nginx/nginx.conf
RUN systemclt start nginx

COPY uwsgi.ini /lavaland/
COPY app/ /lavaland/
CMD uwsgi --ini /lavaland/uwsgi.ini
