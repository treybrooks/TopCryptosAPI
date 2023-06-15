FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY ./ /code/

EXPOSE 8080
CMD ["uvicorn", "app.__init__:init_app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
