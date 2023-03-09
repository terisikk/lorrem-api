FROM python:3.8

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY *.py ./

COPY lorrem ./lorrem

RUN mkdir -p ./conf

COPY conf ./conf

CMD ["flask", "--app",  "app", "run", "--host", "0.0.0.0"]
