FROM python:3.13

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app


EXPOSE 5000

# Use flask run so that it respects environment variables and binds to 0.0.0.0
CMD ["python", "app.py"]
