import mechanicalsoup
from datetime import datetime
import argparse

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

'''
 from datetime import date
 import logging
 logging.basicConfig(level=logging.DEBUG)
'''

'''
    Script searches StackOverflow for jobs and sends email/slack notifications notifications containing:
    * job metadata
    * job link
    Script searches job based on search requirements
    A Cron job sets the interval
'''

slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)


def jobsearch_options():

    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', help="Remote {yes/no}", choices=['yes', 'no'])
    parser.add_argument('-t', help="Job related technologies", type=str)
    parser.add_argument('-e', help="Experience", choices=['Junior', 'Senior', 'Mid-Level', 'Lead'])

    args = parser.parse_args()
    r, t, e = args.r, args.t, args.e
    query = ""
    for opt, val in zip(["-r", "-t", "-e"], [r, t, e]):
        print(opt, val)
    if None not in [r, t, e]:
        query = "?q=" + t.replace(" ", "+") + "&r=" + r + "&mxs=" + e

    return query


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

