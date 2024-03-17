# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim-buster

# Install unixODBC
#RUN apt-get update && apt-get install -y unixodbc

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1


# Install the ODBC Driver 17 for SQL Server
RUN apt-get update && apt-get install -y curl gnupg unixodbc-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
#RUN apt-get update
#RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install the ODBC Driver 17 for SQL Server and sqlcmd
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

# Add sqlcmd to the PATH
ENV PATH="$PATH:/opt/mssql-tools/bin"

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Pass values 
ENV AZURE_OPENAI_DEPLOYMENT_NAME=""
ENV AZURE_OPENAI_ENDPOINT=""
ENV AZURE_OPENAI_API_KEY=""
ENV SPEECH_KEY="<speech key>"
ENV SPEECH_REGION="<location>"
ENV server_name = ""
ENV database_name = ""
ENV SQLADMIN_USER = ""
ENV SQL_PASSWORD = ""

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app

COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["python", "--bind", "0.0.0.0:5000", "app:app"]

CMD [ "python", "app.py"]