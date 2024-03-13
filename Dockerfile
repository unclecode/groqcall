FROM python:3.11 


# Set working directory to /app
WORKDIR /app 

ADD ./app /app/app
ADD ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir .logs
ADD ./frontend /app/frontend

CMD ["uvicorn", "--app-dir", "app/", "--host", "0.0.0.0", "--port", "8000", "main:app"]

