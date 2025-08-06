FROM python:3.13-slim
LABEL maintainer="sasha2056083@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /trainstation

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /trainstation

CMD ["gunicorn", "trainstation.wsgi:application", "--bind", "0.0.0.0:8000"]

USER my_user