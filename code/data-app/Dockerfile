FROM amancevice/pandas:1.2.2-alpine

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

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "streamlit", "run", "analysis.py" ]