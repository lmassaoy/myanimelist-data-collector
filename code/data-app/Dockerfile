FROM python:3.9-alpine3.12

ARG TZ='America/Sao_Paulo'
ENV DEFAULT_TZ ${TZ}

WORKDIR /app

COPY ./code/python/analysis.py /app
COPY ./code/python/utils/ /app
COPY ./code/data-app/requirements.txt /app

RUN apk upgrade --update \
  && apk add -U tzdata \
  && cp /usr/share/zoneinfo/${DEFAULT_TZ} /etc/localtime \
  && apk del tzdata \
  && rm -rf \
  /var/cache/apk/*

RUN apk add --no-cache --update \
  python3 python3-dev gcc \
  gfortran musl-dev g++ \
  libffi-dev openssl-dev \
  libxml2 libxml2-dev \
  libxslt libxslt-dev \
  libjpeg-turbo-dev zlib-dev

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade cython
RUN pip3 install -r requirements.txt

CMD [ "streamlit", "run", "analysis.py" ]