FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY requirements.txt /app
RUN python3 -m pip install -r /app/requirements.txt
COPY ./app /app
