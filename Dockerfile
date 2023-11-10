FROM python:3.11-slim
COPY ./requirements-with-tradingbot.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY db.py run.py /app/
WORKDIR /app
CMD ["python", "run.py"]