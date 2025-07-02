FROM python:3.13.5-slim
WORKDIR /supply-chain
COPY . /supply-chain
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "3 - Data consumption"]

#docker build --no-cache -t supply-chain-datascientest .

#docker run -d --name supply-chain-datascientest-container -e ES_HOST=https://54.78.7.152:9200 -p 8000:8000 lucadigennaro/supply-chain-datascientest

#docker login

#docker push lucadigennaro/supply-chain