
In this project, I will show how you can use web scrapers to search for jobs online. Web scraping is the process of extracting relevant data from online data sources. You can use web scrapers to build datasets when there is no public data available or search for specific information.

The web scraper is built in Python, and packaged in a docker container.
The scraper searches the StackOverflow website for specific jobs and sends notifications to slack. The user associated with the slack account and channel will get an email as a notification with the job links and short job description.

The user can execute the script on demand, at a specific time using crontab or by deploying a docker app.


### Technology stack:
* Python 3.8.5  
* conda 4.8.5  
* slack 4.9.1  
* Docker 19.03.13  

### What is Slack

[Slack](https://slack.com/intl/en-ro/help/articles/115004071768-What-is-Slack-) is a channel-based messaging platform. With Slack, people can work together more effectively, connect all their software tools and services, and find the information they need to do their best work — all within a secure, enterprise-grade environment.
In simple words, slack is a productivity environment.

### Virtualize Python

It's a common practice to have multiple python versions with different libraries installed on a host. The reason behind this is that you keep everything nice and compact for a project. You only install the necessary packages without impacting other virtual environments. Another benefit is that the environment can be exported and easily installed on other mediums. For this, I use conda and pip.   
Conda is an open-source package management system and environment management system for installing multiple versions of software packages and their dependencies and switching between them.     
Pip is a package installer for Python.  

### Script Utilization options

1) The script can be executed on demand using python as an interpreter and supling the job search options

```
python web_scraper_v2.py -r yes -t "python django" -e Junior
Job report generated at: Thursday, 15. October 2020 05:53PM
-r yes
-t python django
-e Junior
https://stackoverflow.com/jobs/165665/python-developer-backend-energyworx
https://stackoverflow.com/jobs/443603/backend-developer-python-django-5-monkeys-agency-ab
https://stackoverflow.com/jobs/443604/backend-developer-python-django-5-monkeys-agency-ab
https://stackoverflow.com/jobs/361172/python-django-software-developer-m-f-d-climatepartner
```

2) Creating an cron job

With cron jobs you can define the specific time when the script will get executed, or you can setup multiple jobs specific searches.

```
### job crawler script

#SLACK_BOT_TOKEN="slack_api_token"
#home_dir="/script_home_location"
#py="python_env_exec_path"
#53 * * * * conda activate "env"; $py  $home_dir/web_scraper.py -r yes -t "python docker" -e Junior >>$home_d>
```

3) The application can be packaged inside a docker app with a cron job and executed at specified intervals.

### Dockerfile

```
FROM python:3.8

# Create app directory
WORKDIR /code

# Install app dependencies

ENV SLACK_BOT_TOKEN="slack_api_token"
COPY requirements_scraper.txt requirements.txt
COPY web_scraper.py .
RUN chmod a+x web_scraper.py
RUN pip install -r requirements.txt

RUN apt-get update && apt-get -y install cron
ADD crontab .
RUN chmod a+x web_scraper.py

RUN crontab crontab
ENTRYPOINT cron -f
```


### Environment installation

```
conda create -n "name_of_the_env" python=3.8

# install python packages
pip install mechanicalsoup
pip install slack_sdk

# export environment 
pip freeze >> reuiremente_scraper.txt
```


Python comes with default libraries, but for this specific project, we must load additional ones.

|   Libary	|   Purpose	|
|:-:	|:-:	|
|   mechanicalsoup| scraping library   	|
|   datetime	| timestamping script execution  	|
|   argparse	| to handle command-line atrributes  	|
|   slack_sdk	| python-slack integration  	|


```
import mechanicalsoup
from datetime import datetime
import argparse

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
```
The script has several functions that solve specific tasks. The **jobsearch_options** takes the job parameters from the user and uses them as arguments in the job search:    
* is the job remote {yes/no}
* technologies/keywords (Python; Docker; AWS)
* experience level (Junior, Mid-Level)

### Get search options

```
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', help="Remote {yes/no}", choices=['yes', 'no'])
    parser.add_argument('-t', help="Job related technologies", type=str)
    parser.add_argument('-e', help="Experience", choices=['Junior', 'Senior', 'Mid-Level', 'Lead'])

    args = parser.parse_args()
    r, t, e = args.r, args.t, args.e
    query=""
    for opt, val in zip(["-r", "-t", "-e"], [r, t, e]):
        print(opt, val)
    if None not in [r, t, e]:
        query = "?q=" + t.replace(" ", "+") + "&r=" + r + "&mxs=" + e

    return query
```
The **get_joblinks** function extracts the links for specific jobs. The link for the job is constructed by appending to a base **base_url = "https://stackoverflow.com/jobs/"** + **job-specific** links.  
One must know, at least in broad terms, the elements that make up a web page. It is important for understanding how the script works.  

For the most part, within a web page, you can find these technologies:

|   Technologies	|   Description	|
|:-:	|:-:	|
| HTML | HTML is the standard markup language for creating Web pages |
| CSS |  Cascading Style Sheets |
| JavaScript | JavaScript is one of the most used Web programming languages |

HTML describes the structure of a Web page. Within a Web page, elements called tags tell the browser how to display the content. The elements of a web page are nested within other elements.   
With CSS you control the styling and the layout of the page.   

We can find out the hierachy of an element in a web page by right-clicking the element and selecting inspect element. The job requirements are located within structures as seen below:

```
<h2>
    <a>
        <href> link </href>
    <a/>
<h2/>
```

![IMG](/Img/inspect_link.png)

```
def get_jobslinks(start, url):
    browser = mechanicalsoup.StatefulBrowser()
    try:
        browser.open(url)
    except:
        exit("unable to open {}".format(url))

    job_info = browser.get_current_page().find_all("h2")
    jobs = []
    for elem in job_info:
        links = elem.find_all("a")
        for item in links:
            job = item.get("href")
            job = job.replace("/jobs", "")
            jobs.append(start + job)

    browser.close()
    return jobs
```

The **get_jobmeta** function extracts job-specific information. The information is available on the div element, mb8 CSS class. We can use the same principle and inspect the element in the browser. From these elements, the text is extracted and sent to the Slack bot in the next function.


### Job requirement example

![IMG](/Img/job_desc.png)

```
def get_jobmeta(job_lists):
    browser = mechanicalsoup.StatefulBrowser()
    job_req = ""

    time = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    job_req = job_req+"Job report generated at: " + time + "\n\n"

    for job in job_lists:
        print(job)
        job_req = job_req + job
        try:
            browser.open(job)
        except:
            exit("unable to open {}". format(job))

        job_info = browser.get_current_page().find_all("div", class_="mb8")
        # job_tech = browser.get_current_page().find_all("div", class_="mb16")

        for i in range(1, len(job_info)):
            job_req = job_req + job_info[i].text

        job_req += "#"*50 + " NEXT JOB " + "#"*50 + "\n"

    browser.close()
    return job_req

```

The below function sends the job compiled data to the slack channel. The slack channel, as well as the bot that will post the job description to the chat, must be specified.


```
def send_jobinfo(job):
    try:
        response = client.chat_postMessage(
            channel="job_search",
            text=job,
            user="bot_job"
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]
```

The main function, although not needed, helps us to invoke the functions during run-time or when the program is executed.

```
if __name__ == "__main__":
    time_cli = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    print("Job report generated at: {}".format(time_cli))
    # define job search
    q = jobsearch_options()

    # general url
    base_url = "https://stackoverflow.com/jobs"
    start_url = base_url + q

    job_links = get_jobslinks(base_url, start_url)
    jobs_specs = get_jobmeta(job_links)

    send_jobinfo(jobs_specs)
```


