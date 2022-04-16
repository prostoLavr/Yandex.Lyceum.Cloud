FROM ubuntu
RUN apt-get install -y apt-utils
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
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
