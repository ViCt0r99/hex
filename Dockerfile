FROM python:3.11-buster

RUN pip3 install pipenv

# Create app directory
WORKDIR /app

# -- Adding Pipfiles
COPY ./src/Pipfile Pipfile
COPY ./src/Pipfile.lock Pipfile.lock

# -- Install dependencies:
RUN set -ex && pipenv install --system --dev --ignore-pipfile

# Bundle app source
COPY . .

# Expose port
EXPOSE 8000

CMD ["python3", "src/manage.py", "migrate"]
CMD ['python3', "src/manage.py", "collectstatic", "--noinput"]
CMD ["python3", "src/manage.py", "runserver", "0.0.0.0:8000"]