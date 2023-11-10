FROM python:3.11-slim
RUN apt update && apt install -y git cmake build-essential libopenblas-dev
RUN git clone https://github.com/robertmartin8/PyPortfolioOpt /tmp/PyPortfolioOpt
WORKDIR /tmp/PyPortfolioOpt
RUN pip install -e /tmp/PyPortfolioOpt
RUN rm -rf /tmp/PyPortfolioOpt
COPY ./requirements-with-tradingbot.txt /app/requirements-with-tradingbot.txt
RUN pip install -r /app/requirements-with-tradingbot.txt
RUN apt remove -y git cmake build-essential libopenblas-dev && apt autoremove -y
# copy files
COPY db.py run.py /app/
WORKDIR /app
CMD ["python", "run.py"]