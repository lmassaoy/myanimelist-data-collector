FROM python:3.9.2-slim

WORKDIR /app

COPY ./code/python/analysis.py /app
COPY ./code/python/utils/ /app/utils/
COPY ./code/data-app/requirements.txt /app

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade cython
RUN pip3 install -r requirements.txt

CMD [ "streamlit", "run", "analysis.py" ]