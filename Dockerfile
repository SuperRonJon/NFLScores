FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

ENV PORT=8000

ENV MONGODB_URI="mongodb://db:27017/"

EXPOSE  8000

CMD ["python", "app.py"]