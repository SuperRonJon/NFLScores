FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

ENV PORT=8000

ENV MONGODB_URI="mongodb://localhost:27017/"

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0", "app:app"]