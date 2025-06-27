FROM python:3.13.5-slim
WORKDIR /supply-chain
COPY . /supply-chain
RUN pip install --no-cache-dir -r requirements.txt