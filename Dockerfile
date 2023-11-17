FROM python:3.11-slim
RUN apt update && apt install -y git build-essential libopenblas-dev cmake
RUN pip install git+https://github.com/robertmartin8/PyPortfolioOpt
RUN pip install cvxpy
COPY ./requirements-with-tradingbot.txt /app/requirements-with-tradingbot.txt
RUN pip install -r /app/requirements-with-tradingbot.txt
RUN apt remove -y git build-essential cmake && apt autoremove -y
# copy files
COPY db.py run.py /app/
WORKDIR /app
CMD ["python", "run.py"]