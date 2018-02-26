FROM python:3

WORKDIR /app

ADD requirements.txt /app

ENTRYPOINT ["/app/docker-entrypoint.sh"]

RUN pip install -r requirements.txt

ADD app.py /app
ADD rest.py /app
ADD migrate.py /app
ADD docker-entrypoint.sh /app

CMD ["python", "/app/migrate.py"]
