FROM python:3.6

WORKDIR /client

COPY . /client

RUN pip install requests

EXPOSE 80

CMD python3 client.py $ip_app
