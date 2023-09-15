FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

ENV PORT=8000

ENV MONGODB_URI="mongodb://db:27017/"

EXPOSE  8000

CMD ["python", "app.py"]

# For linux serving
# CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0", "app:app"]

# For windows serving - waitress needs to be added to requirements.txt and installed to use this
# CMD ["waitress-serve", "--port=8000","app:app"]