FROM python:3.12

WORKDIR /usr/src/app

ADD main.py requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
