FROM python:3.11-alpine

WORKDIR /code

RUN apk update && apk upgrade
RUN apk add --no-cache gcc \
                       libpq-dev build-base \
                       linux-headers \
                       postgresql postgresql-dev python3-dev musl-dev \
    && rm -rf /var/cache/apk/*

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

COPY ./ /code/

EXPOSE 8080
CMD ["uvicorn", "app.__init__:init_app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
