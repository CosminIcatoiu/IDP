FROM python:3.6

EXPOSE 80

WORKDIR /service

COPY requirements.txt /service
RUN pip install -r requirements.txt

COPY service.py /service
CMD python service.py
