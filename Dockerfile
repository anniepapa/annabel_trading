FROM python:3.9-slim
RUN mkdir /app 
COPY . /app
COPY poetry.lock pyproject.toml /app/
WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:source/
ENV PORT 8080
EXPOSE 8080
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

ENTRYPOINT ["python", "source/main.py"]
RUN apt-get update && apt-get install -y bash
