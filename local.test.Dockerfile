FROM airbnb-playwright-base

WORKDIR /app

COPY src ./src
COPY tests ./tests
COPY pytest.ini .
COPY pytest_runner.py .

CMD ["tail", "-f", "/dev/null"]