FROM python:3.11-slim
# RUN apt update && apt install build-essential cmake -y
COPY ./requirements-with-tradingbot.txt /app/requirements-with-tradingbot.txt
RUN pip install -r /app/requirements-with-tradingbot.txt
COPY db.py run.py /app/
WORKDIR /app
CMD ["python", "run.py"]