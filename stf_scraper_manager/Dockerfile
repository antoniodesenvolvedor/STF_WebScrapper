FROM python:3


RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && apt-get install nginx unixodbc unixodbc-dev \
    python-pyodbc libsqliteodbc vim -y --no-install-recommends

RUN ACCEPT_EULA=Y apt-get install msodbcsql17

COPY . .
RUN pip install -r requirements.txt

CMD ["python","-u","./manage.py","runserver","0.0.0.0:8000"]