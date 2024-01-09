# -*- coding: utf-8 -*-
"""
This app monitors your internet connection and generates prometheus metrics.
"""
import datetime
import logging
import os
import sys

import requests
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BlockingScheduler
from icmplib import ping
from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
from prometheus_client.utils import INF
from pytz import utc

from im.config import CONFIG

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
    """Calculate the internet latency stats based on ICMP.

    This method uses icmp echo request/response and calculate the average rtt, packet loss and jitter.

    Args:
        dest (string): hostname or IP address

    """

    PING_REQUESTS.inc()
    try:
        with PING_FAILURES.count_exceptions():
            LOGGER.debug("PING - destination: " + str(dest))
            host = ping(str(dest), count=2, interval=0.5)
        PING_LATENCY.observe(host.avg_rtt / 1000)
        PING_PACKET_LOSS.inc(host.packet_loss)
        PING_JITTER.set((host.max_rtt - host.min_rtt) / 1000)
        LOGGER.debug("PING - max_rtt: " + str(host.max_rtt))
        LOGGER.debug("PING - min_rtt: " + str(host.min_rtt))
        LOGGER.debug("PING - avg_rtt: " + str(host.avg_rtt))
        LOGGER.debug("PING - packet_loss: " + str(host.packet_loss))
        UP.set(1)
    except Exception as e:
        LOGGER.error("Could not process ICMP Echo requests: %s", e)
        UP.set(0)


@DOWNLOAD_DURATION.time()
def download_speed(url):
    """
    Calculates the download speed based request size and the time it takes
    """
    DOWNLOAD_REQUESTS.inc()

    try:
        LOGGER.info("downloading a file...")
        resp = requests.get(url)
        DOWNLOAD_REQUEST_SIZE.set(len(resp.content))
    except Exception:
        LOGGER.error("Cannot download the file %s", url)
        DOWNLOAD_FAILURES.inc()


@UPLOAD_DURATION.time()
def upload_speed(url):
    """
    Calculates the upload speed based on http POST method
    """
    UPLOAD_REQUESTS.inc()
    try:
        files = {"file": open("test-upload", "rb")}
        requests.post(url, files=files)
        UPLOAD_REQUEST_SIZE.set(os.stat("test-upload").st_size)
    except Exception:
        LOGGER.error("Cannot upload the file")
        UPLOAD_FAILURES.inc()


def job_scheduler(config):  # pragma: no cover
    """
    Setup logging, start the job scheduler and serve prometheus metrics
    """

    LOGGER.info("Sarting application at http://localhost:8000")

    executors = {
        "default": ThreadPoolExecutor(5),
    }
    job_defaults = {"coalesce": False, "max_instances": 5}

    scheduler = BlockingScheduler(
        executors=executors, job_defaults=job_defaults, timezone=utc
    )

    scheduler.add_job(
        func=download_speed,
        trigger="interval",
        max_instances=1,
        seconds=config["jobs"]["download"]["interval"],
        args=[config["downloadURL"]],
        id="download_speed",
        next_run_time=datetime.datetime.utcnow(),
        start_date=datetime.datetime.utcnow(),
    )

    scheduler.add_job(
        func=latency,
        trigger="interval",
        seconds=config["jobs"]["ping"]["interval"],
        args=[config["icmpDestHost"]],
        id="ping",
        next_run_time=datetime.datetime.utcnow(),
        start_date=datetime.datetime.utcnow(),
    )

    # create temporary upload file
    with open("test-upload", "wb") as out:
        out.truncate(1024 * 1024 * 50)

    scheduler.add_job(
        func=upload_speed,
        trigger="interval",
        seconds=config["jobs"]["upload"]["interval"],
        args=[config["uploadURL"]],
        id="upload_speed",
        next_run_time=datetime.datetime.utcnow(),
        start_date=datetime.datetime.utcnow(),
    )

    # start prometheus server to serve /metrics and /describe endpoints
    start_http_server(addr="0.0.0.0", port=8000)  # nosec
    scheduler.start()


def main():  # pragma: no cover
    """
    Start up scheduler and logging facilities.
    """

    # load app configuration

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

    LOGGER.debug("PYTHONPATH: %s", sys.path)
    try:
        job_scheduler(CONFIG)
    except KeyboardInterrupt:
        LOGGER.info("Shutting down internet-monitor...")
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
