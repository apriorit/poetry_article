# First build stage: build the application
FROM python:3.10-buster as py-build

# Install poetry for package management
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

# Copy the entire application to the container and set the working directory
WORKDIR /app
COPY . .

# Second build stage: run the application
FROM python:3.10-slim-buster as py-run

# Copy the poetry directory from the first build stage to the second build stage
COPY --from=py-build /opt/poetry /opt/poetry

# Add the poetry bin directory to the PATH
ENV PATH=/opt/poetry/bin:$PATH

# Copy the application code from the first build stage to the second build stage
COPY --from=py-build /app /app

# Create a new user for running the application and set the ownership of the app directory
RUN useradd -ms /bin/bash myuser
RUN chown -R myuser:myuser /app
USER myuser

#Install dependencies using Poetry
WORKDIR /app/Microservices/OrderManager
RUN poetry install

# Start the application using poetry run
CMD ["poetry", "run", "python", "order_manager/main.py"]