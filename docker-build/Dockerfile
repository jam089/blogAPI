FROM python:3.12.10-bookworm
EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==2.1.2"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY app .

RUN chmod +x prestart.sh
RUN chmod +x run

ENTRYPOINT ["./prestart.sh"]
CMD ["./run"]