FROM python:3.8

# Create app directory
WORKDIR /code

# Install app dependencies

ENV SLACK_BOT_TOKEN="api_generated_token"
COPY requirementtxt .
COPY web_scraper.py .
RUN chmod a+x web_scraper.py
RUN pip install -r requirements.txt

RUN apt-get update && apt-get -y install cron nano
ADD crontab .
RUN chmod a+x web_scraper.py

RUN crontab crontab
ENTRYPOINT cron -f


# Uncomment if you want to run the script if docker container starts

#CMD ["python", "web_scraper.py", "-r", "yes", "-t", "python docker", "-e", "Junior"]
