FROM python:3.12.0-slim-bullseye
WORKDIR /app
# COPY ./requirements.txt /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
ENV FLASK_APP=app.py
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "8080"]
