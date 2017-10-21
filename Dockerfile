FROM python:3.5-slim
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

#Install nano for logs
RUN apt-get update
RUN apt-get install nano

# Port 4000 is the control server by default
EXPOSE 4000

CMD ["python", "PingRelay.py"]
