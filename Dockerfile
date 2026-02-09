FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the full project into the image (keeps caching for requirements above)
COPY . /code

# Start the app by importing the package module so relative imports work
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]

# Build the Docker image with:
# docker build -t webstore .
# Run the Docker container with:
# docker run -d --name webstore_container -p 80:80 -v $(pwd)/app:/code/app webstore

#docker compose up --build && docker compose logs -f backend