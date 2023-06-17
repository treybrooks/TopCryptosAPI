FROM python:3.11-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY ./app /code/app
COPY ./tests /code/tests

EXPOSE 8082
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8082"]
