FROM python:3.9

EXPOSE 8501

WORKDIR /st

COPY ./requirements.txt /st/requirements.txt

RUN pip3 install -r /st/requirements.txt

COPY ./ui /st/ui

ENTRYPOINT ["streamlit", "run", "ui/streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
