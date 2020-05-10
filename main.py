#!/usr/bin/env python3
"""
This app monitors your internet connection and generates prometheus metrics.
"""
import sys
import logging
import requests

from pytz import utc
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from prometheus_client import start_http_server, Counter, Gauge, Summary, Histogram
from prometheus_client.utils import INF
from icmplib import ping

# pylint: disable=fixme, broad-except

# metrics definition
PING_REQUESTS = Counter('internet_monitor_ping_total',
                        'Total ping requests made to 1.1.1.1')
PING_FAILURES = Counter('internet_monitor_ping_failures_total',
                        'Total ping requests failed made to 1.1.1.1')
PING_PACKET_LOSS = Gauge('internet_monitor_ping_packet_loss',
                         'Number of packets lost while checking latency')
PING_JITTER = Gauge('internet_monitor_ping_jitter', 'ICMP Jitter')
UP = Gauge('internet_monitor_up', 'Internet is up or down')
PING_LATENCY = Summary(
    'internet_monitor_ping_latency_seconds', 'Ping latency to 1.1.1.1')
DOWNLOAD_DURATION = Histogram('internet_monitor_download_duration_seconds',
                              'Download latency', buckets=(1, 2, 5, 7, 10, 15, 20, 50, 100, INF))
DOWNLOAD_REQUEST_SIZE = Gauge(
    'internet_monitor_download_size_bytes', 'Bytes downloaded')
DOWNLOAD_REQUESTS = Counter(
    'internet_monitor_download_total', 'Number of times the download job runs')
DOWNLOAD_FAILURES = Counter(
    'internet_monitor_download_failures', 'Number of times the download job fails')

def latency(dest):
    """
    Calculate the average rtt time using ICMP echo request
    """

    PING_REQUESTS.inc()
    try:
        with PING_FAILURES.count_exceptions():
            host = ping(dest, count=2, interval=0.5)
        PING_LATENCY.observe(host.avg_rtt / 1000)
        PING_PACKET_LOSS.set(host.packet_loss)
        PING_JITTER.set(host.max_rtt - host.min_rtt)
        UP.set(1)
    except Exception:
        LOGGER.error('Could not process ICMP Echo requests.')
        UP.set(0)


@DOWNLOAD_DURATION.time()
def download_speed(url):
    """
    Calculates the download speed based request size and the time it takes
    """
    DOWNLOAD_REQUESTS.inc()

    # url = 'http://212.183.159.230/512MB.zip'

    try:
        resp = requests.get(url)
        DOWNLOAD_REQUEST_SIZE.set(len(resp.content))

    except Exception:
        LOGGER.error('Cannot download the file %s', url)
        DOWNLOAD_FAILURES.inc()


# runs once every minute
def upload_speed():
    """
    Calculates the upload speed based on http POST method
    """


def main():
    """
    Setup logging, start the job scheduler and serve prometheus metrics
    """

    LOGGER.info('Sarting application at http://localhost:8000')

    executors = {
        'default': ThreadPoolExecutor(20),
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }

    scheduler = BlockingScheduler(
        executors=executors, job_defaults=job_defaults, timezone=utc)

    url = "http://212.183.159.230/512MB.zip"
    latency_dest = '1.1.1.1'
    scheduler.add_job(download_speed, 'interval', seconds=600,
                      args=[url], id='download_speed')
    scheduler.add_job(latency, 'interval', seconds=60,
                      args=[latency_dest], id='ping')

    # start prometheus server to serve /metrics and /describe endpoints
    start_http_server(8000)
    scheduler.start()


if __name__ == '__main__':

    # Setting up logging
    LOGGER = logging.getLogger('internet.monitor')
    LOGGER.setLevel(logging.INFO)
    # create console handler with a higher log level
    CH = logging.StreamHandler()
    CH.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    CH.setFormatter(FORMATTER)
    # add the handlers to the LOGGER and apscheduler LOGGER
    LOGGER.addHandler(CH)
    logging.getLogger('apscheduler.executors.default').addHandler(CH)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.INFO)

    try:
        main()
    except KeyboardInterrupt:
        LOGGER.info('Shutting down internet-monitor...')
        sys.exit(0)
