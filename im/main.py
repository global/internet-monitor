#!/usr/bin/env python3
"""
This app monitors your internet connection and generates prometheus metrics.
"""
import sys
import os
import logging
import requests
import yaml
import datetime

from pytz import utc
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from prometheus_client import start_http_server, Counter, Gauge, Summary, Histogram
from prometheus_client.utils import INF
from icmplib import ping

# ping metrics
PING_REQUESTS = Counter(
    "internet_monitor_ping_total", "Total ping requests made to 1.1.1.1"
)
PING_FAILURES = Counter(
    "internet_monitor_ping_failures_total", "Total ping requests failed made to 1.1.1.1"
)
PING_PACKET_LOSS = Counter(
    "internet_monitor_ping_packet_loss_total",
    "Number of packets lost while checking latency",
)
PING_JITTER = Gauge("internet_monitor_ping_jitter_seconds", "ICMP Jitter")
UP = Gauge("internet_monitor_up", "Internet is up or down")
PING_LATENCY = Summary(
    "internet_monitor_ping_latency_seconds", "Ping latency to 1.1.1.1"
)

# download metrics
DOWNLOAD_DURATION = Histogram(
    "internet_monitor_download_duration_seconds",
    "Download latency",
    buckets=(1, 2, 5, 7, 10, 15, 20, 50, 100, INF),
)
DOWNLOAD_REQUEST_SIZE = Gauge(
    "internet_monitor_download_size_bytes", "Bytes downloaded"
)
DOWNLOAD_REQUESTS = Counter(
    "internet_monitor_download_total", "Number of times the download job runs"
)
DOWNLOAD_FAILURES = Counter(
    "internet_monitor_download_failures_total", "Number of times the download job fails"
)

# upload metrics
UPLOAD_DURATION = Histogram(
    "internet_monitor_upload_duration_seconds",
    "Upload latency",
    buckets=(1, 2, 5, 7, 10, 15, 20, 50, 100, INF),
)
UPLOAD_REQUESTS = Counter(
    "internet_monitor_upload_total", "Number of times the upload job runs"
)
UPLOAD_FAILURES = Counter(
    "internet_monitor_upload_failures_total", "Number of times the upload job fails"
)
UPLOAD_REQUEST_SIZE = Gauge("internet_monitor_upload_size_bytes", "Bytes uploaded")

LOGGER = logging.getLogger("internet.monitor")


def latency(dest):
    """
    Calculate the average rtt time using ICMP echo request
    """

    PING_REQUESTS.inc()
    try:
        with PING_FAILURES.count_exceptions():
            host = ping(dest, count=2, interval=0.5)
        PING_LATENCY.observe(host.avg_rtt / 1000)
        PING_PACKET_LOSS.inc(host.packet_loss)
        PING_JITTER.set((host.max_rtt - host.min_rtt) / 1000)
        UP.set(1)
    except Exception as e:
        LOGGER.error("Could not process ICMP Echo requests.")
        print(e)
        UP.set(0)


@DOWNLOAD_DURATION.time()
def download_speed(url):
    """
    Calculates the download speed based request size and the time it takes
    """
    DOWNLOAD_REQUESTS.inc()

    try:
        resp = requests.get(url)
        DOWNLOAD_REQUEST_SIZE.set(len(resp.content))

    except Exception:
        LOGGER.error("Cannot download the file %s", url)
        DOWNLOAD_FAILURES.inc()


@UPLOAD_DURATION.time()
def upload_speed():
    """
    Calculates the upload speed based on http POST method
    """
    UPLOAD_REQUESTS.inc()
    try:
        files = {"file": open("test-upload", "rb")}
        requests.post("https://file.io/?expires=1d", files=files)
        UPLOAD_REQUEST_SIZE.set(os.stat("test-upload").st_size)
    except Exception:
        LOGGER.error("Cannot upload the file")
        UPLOAD_FAILURES.inc()


def load_configuration(filename):
    """
    Load YAML configuration file and return a dict
    """
    with open(filename) as conf:
        return yaml.load(conf, Loader=yaml.FullLoader)


def main(config):
    """
    Setup logging, start the job scheduler and serve prometheus metrics
    """

    LOGGER.info("Sarting application at http://localhost:8000")

    executors = {
        "default": ThreadPoolExecutor(5),
    }
    job_defaults = {"coalesce": False, "max_instances": 3}

    scheduler = BlockingScheduler(
        executors=executors, job_defaults=job_defaults, timezone=utc
    )

    start_job_date = datetime.datetime.now() - datetime.timedelta(seconds=590)
    scheduler.add_job(
        download_speed,
        "interval",
        seconds=600,
        args=[config["downloadURL"]],
        id="download_speed",
        start_date=start_job_date,
    )

    start_job_date = datetime.datetime.now() - datetime.timedelta(seconds=50)
    scheduler.add_job(
        latency,
        "interval",
        seconds=60,
        args=[config["icmpDestHost"]],
        id="ping",
        start_date=start_job_date,
    )

    # create temporary upload file
    with open("test-upload", "wb") as out:
        out.truncate(1024 * 1024 * 50)

    start_job_date = datetime.datetime.now() - datetime.timedelta(seconds=3590)
    scheduler.add_job(
        upload_speed,
        "interval",
        seconds=3600,
        id="upload_speed",
        start_date=start_job_date,
    )

    # start prometheus server to serve /metrics and /describe endpoints
    start_http_server(addr="0.0.0.0", port=8000)
    scheduler.start()


if __name__ == "__main__":

    # load app configuration
    CONFIG = load_configuration("monitor.yml")

    # Setting up logging
    LOGGER.setLevel(CONFIG["logLevel"])
    # create console handler with a higher log level
    CH = logging.StreamHandler()
    CH.setLevel(CONFIG["logLevel"])
    # create formatter and add it to the handlers
    FORMATTER = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    CH.setFormatter(FORMATTER)
    # add the handlers to the LOGGER and apscheduler LOGGER
    LOGGER.addHandler(CH)
    logging.getLogger("apscheduler.executors.default").addHandler(CH)
    logging.getLogger("apscheduler.executors.default").setLevel(CONFIG["logLevel"])

    try:
        main(CONFIG)
    except KeyboardInterrupt:
        LOGGER.info("Shutting down internet-monitor...")
        sys.exit(0)
