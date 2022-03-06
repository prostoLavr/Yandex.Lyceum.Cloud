FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash vim 
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
RUN pip install --upgrade pip
RUN pip install setuptools
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install --no-cache-dir -r /var/www/requirements.txt
COPY ./app /app
