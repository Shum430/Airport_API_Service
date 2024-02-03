FROM python:3.11.4-slim-buster
LABEL maintainer="andshumskyy@gmail.com"

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc postgresql-client libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app/

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

RUN mkdir -p /vol/web/media

# Create a non-root user
RUN adduser --disabled-password --no-create-home django-user

RUN chown -R django-user:django-user /vol/
RUN chmod -R 755 /vol/web/
USER django-user

# Command to run the application
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
