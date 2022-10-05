FROM python:3.9-slim
WORKDIR /app
COPY ./ /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
CMD ["./start.sh"]