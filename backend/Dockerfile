FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY . /app
CMD ["./start.sh"]