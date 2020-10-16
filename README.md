# Job-Scraping

Within this project, I will show a prototype of a job scraper.
A python script will scrape the StackOverflow site for job requirements.
This proof of concept project can serve as a starting point for other web-crawlers/web-scrapers.

### Project structure

```
├── crontab
├── Dockerfile
├── Img
│   ├── inspect_link.png
│   ├── job_desc.png
│   ├── jobs_specs.png
│   └── job_url.png
├── Project.md
├── README.md
├── requirements.txt
└── web_scraper.py
```

The script can be executed on-demand, within a cron job, or inside a docker container.
The **requirements.txt** file contains the project-specific packages/libraries.

Project.md explains in more depth the technical aspects.

### Script execution

1) The script can be executed on-demand:

```
python web_scraper.py --help
Job report generated at: Friday, 16. October 2020 06:20AM
usage: web_scraper.py [-h] [-r {yes,no}] [-t T] [-e {Junior,Senior,Mid-Level,Lead}]

optional arguments:
  -h, --help            show this help message and exit
  -r {yes,no}           Remote {yes/no}
  -t T                  Job related technologies
  -e {Junior,Senior,Mid-Level,Lead}
                        Experience
```
2) As part of a cron job:

```
### job crawler script

#SLACK_BOT_TOKEN="slack_api"
#home_dir="script_home_location"
#py="python_install_path"
# {time_of_the_day} * * * * conda activate py37_covidenv; $py  $home_dir/web_scraper.py -r yes -t "python docker" -e Junior >>$home_dir/cron_exec.txt 2>&1
```

3) Containerize the script within a Dockerfile

```
docker build --rm -f Dockerfile_python -t praslea/job_scraper .
docker run -it praslea/job_scraper
```

