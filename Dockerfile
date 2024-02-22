# Use an official Python runtime as a parent image
FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set the working directory in the container to /code
WORKDIR /code

# Add the current directory contents into the container at /code
ADD . /code/

# Install any needed packages specified in requirements.txt
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

# Define a variável de ambiente para o Flask saber onde encontrar o arquivo de configuração
ENV FLASK_APP=app.py

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Comando para executar a aplicação Flask quando o contêiner for iniciado
# CMD ["flask", "run", "--host=0.0.0.0"]
