FROM python:3.10

COPY . ./app

WORKDIR /app

RUN pip install virtualenv

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]

