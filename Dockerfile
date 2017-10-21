FROM python:3.5-slim
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

# Port 8080 is the control server by default
EXPOSE 8080

CMD ["python", "PingRelay.py"]
