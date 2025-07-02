FROM python:latest

# Install Node.js and npm
RUN apt-get update && apt-get install -y wget curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

RUN wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz
RUN tar -C /usr/local/bin -xzf dockerize-linux-amd64-v0.6.1.tar.gz

WORKDIR /app

COPY requirements.txt .
COPY package.json .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
RUN npm install

COPY . .

# Build Tailwind CSS
RUN npx tailwindcss -i ./static/main.css -o ./static/output.css --minify

EXPOSE 8000

ENTRYPOINT ["dockerize", "-wait", "tcp://mysql:3306", "-wait", "tcp://redis:6379", "-timeout", "60s"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]