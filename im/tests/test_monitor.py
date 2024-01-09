import random
from importlib import reload
from unittest.mock import Mock, patch

import pytest
from prometheus_client import REGISTRY

from im import monitor


@pytest.fixture
def icmp_mocked_host():
    mock = Mock()
    mock.avg_rtt = random.randint(1, 10)
    mock.packet_loss = random.randint(0, 10)
    mock.max_rtt = random.randint(1, 5)
    mock.min_rtt = random.randint(5, 10)

    return mock


def clean_prometheus_registry():
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)


def test_latency(icmp_mocked_host):
    """
    Test if ping succeeds and generates the right metrics.
    """

    clean_prometheus_registry()
    reload(monitor)

    before_up = REGISTRY.get_sample_value("internet_monitor_up")
    before_ping_total = REGISTRY.get_sample_value("internet_monitor_ping_total")
    before_ping_packet_loss_total = REGISTRY.get_sample_value(
        "internet_monitor_ping_packet_loss_total"
    )
    before_ping_jitter_seconds = REGISTRY.get_sample_value(
        "internet_monitor_ping_jitter_seconds"
    )
    before_ping_latency_seconds = REGISTRY.get_sample_value(
        "internet_monitor_ping_latency_seconds"
    )

    assert before_up == 0
    assert before_ping_total == 0
    assert before_ping_packet_loss_total == 0
    assert before_ping_jitter_seconds == 0

    with patch("im.monitor.ping") as mock_ping:
        mock_ping.return_value = icmp_mocked_host
        monitor.latency("1.1.1.1")

    after_up = REGISTRY.get_sample_value("internet_monitor_up")
    after_ping_total = REGISTRY.get_sample_value("internet_monitor_ping_total")
    after_ping_packet_loss_total = REGISTRY.get_sample_value(
        "internet_monitor_ping_packet_loss_total"
    )
    after_ping_jitter_seconds = REGISTRY.get_sample_value(
        "internet_monitor_ping_jitter_seconds"
    )
    after_ping_latency_seconds = REGISTRY.get_sample_value(
        "internet_monitor_ping_latency_seconds_sum"
    )

    assert after_up == 1
    assert after_ping_total == 1
    assert after_ping_packet_loss_total == icmp_mocked_host.packet_loss
    assert (
        after_ping_jitter_seconds
        == (icmp_mocked_host.max_rtt - icmp_mocked_host.min_rtt) / 1000
    )
    assert after_ping_latency_seconds == icmp_mocked_host.avg_rtt / 1000


def test_latency_failure(icmp_mocked_host):
    """
    Test if ping fails and generates the right metrics.
    """

    clean_prometheus_registry()
    reload(monitor)

    before_up = REGISTRY.get_sample_value("internet_monitor_up")
    before_ping_total = REGISTRY.get_sample_value("internet_monitor_ping_total")
    before_ping_failures_total = REGISTRY.get_sample_value(
        "internet_monitor_ping_failures_total"
    )

    assert before_up == 0
    assert before_ping_total == 0
    assert before_ping_failures_total == 0

    with patch("im.monitor.ping") as mock_ping:
        mock_ping.side_effect = Exception("boom!")
        monitor.latency("1.1.1.1")

    after_up = REGISTRY.get_sample_value("internet_monitor_up")
    after_ping_total = REGISTRY.get_sample_value("internet_monitor_ping_total")
    before_ping_failures_total = REGISTRY.get_sample_value(
        "internet_monitor_ping_failures_total"
    )

    assert after_up == 0
    assert after_ping_total == 1
    assert before_ping_failures_total == 1


@pytest.fixture
def http_mocked_response():
    mock = Mock()
    mock.content = "ok"
    return mock


def test_download_speed(http_mocked_response):
    """
    Test if download succeeds and calculates the appropriate size and successfull job execution.
    """

    clean_prometheus_registry()
    reload(monitor)

    before_download_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_download_duration_seconds_sum"
    )
    before_download_size_bytes = REGISTRY.get_sample_value(
        "internet_monitor_download_size_bytes"
    )
    before_download_total = REGISTRY.get_sample_value("internet_monitor_download_total")

    assert before_download_duration_seconds_sum == 0
    assert before_download_size_bytes == 0
    assert before_download_total == 0

    with patch("im.monitor.requests") as mocked_requests:
        mocked_requests.get.return_value = http_mocked_response
        monitor.download_speed("http://localhost")

    after_download_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_download_duration_seconds_sum"
    )
    after_download_size_bytes = REGISTRY.get_sample_value(
        "internet_monitor_download_size_bytes"
    )
    after_download_total = REGISTRY.get_sample_value("internet_monitor_download_total")

    assert isinstance(after_download_duration_seconds_sum, float)
    assert after_download_size_bytes == len(http_mocked_response.content)
    assert after_download_total == 1


def test_download_speed_failures(http_mocked_response):
    """
    Test if download fails and failure metrics are updated accordingly.
    """

    clean_prometheus_registry()
    reload(monitor)

    before_download_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_download_duration_seconds_sum"
    )
    before_download_failures_total = REGISTRY.get_sample_value(
        "internet_monitor_download_failures_total"
    )
    before_download_total = REGISTRY.get_sample_value("internet_monitor_download_total")

    assert before_download_duration_seconds_sum == 0
    assert before_download_failures_total == 0
    assert before_download_total == 0

    with patch("im.monitor.requests") as mocked_requests:
        mocked_requests.get.side_effect = Exception("boom!")
        monitor.download_speed("http://localhost")

    after_download_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_download_duration_seconds_sum"
    )
    after_download_failures_total = REGISTRY.get_sample_value(
        "internet_monitor_download_failures_total"
    )
    after_download_total = REGISTRY.get_sample_value("internet_monitor_download_total")

    assert isinstance(after_download_duration_seconds_sum, float)
    assert after_download_failures_total == 1
    assert after_download_total == 1


def test_upload_speed(http_mocked_response):
    """
    Test if upload succeeds and calculates the appropriate size and successfull job execution.
    """

    clean_prometheus_registry()
    reload(monitor)

    before_upload_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_upload_duration_seconds_sum"
    )
    before_upload_size_bytes = REGISTRY.get_sample_value(
        "internet_monitor_upload_size_bytes"
    )
    before_upload_total = REGISTRY.get_sample_value("internet_monitor_upload_total")

    assert before_upload_duration_seconds_sum == 0
    assert before_upload_size_bytes == 0
    assert before_upload_total == 0

    with patch("im.monitor.requests") as mocked_requests:
        with patch("im.monitor.os.stat") as mocked_stat:
            mocked_requests.post.return_value = http_mocked_response
            mocked_stat.return_value.st_size = len(http_mocked_response.content)
            monitor.upload_speed("http://localhost")

    after_upload_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_upload_duration_seconds_sum"
    )
    after_upload_size_bytes = REGISTRY.get_sample_value(
        "internet_monitor_upload_size_bytes"
    )
    after_upload_total = REGISTRY.get_sample_value("internet_monitor_upload_total")

    assert isinstance(after_upload_duration_seconds_sum, float)
    assert after_upload_size_bytes == len(http_mocked_response.content)
    assert after_upload_total == 1


def test_upload_speed_failures(http_mocked_response):
    """
    Test if upload fails and failure metrics are updated accordingly.
    """

    clean_prometheus_registry()
    reload(monitor)

    before_upload_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_upload_duration_seconds_sum"
    )
    before_upload_failures_total = REGISTRY.get_sample_value(
        "internet_monitor_upload_failures_total"
    )
    before_upload_total = REGISTRY.get_sample_value("internet_monitor_upload_total")

    assert before_upload_duration_seconds_sum == 0
    assert before_upload_failures_total == 0
    assert before_upload_total == 0

    with patch("im.monitor.requests") as mocked_requests:
        mocked_requests.post.side_effect = Exception("boom!")
        monitor.upload_speed("http://localhost")

    after_upload_duration_seconds_sum = REGISTRY.get_sample_value(
        "internet_monitor_upload_duration_seconds_sum"
    )
    after_upload_failures_total = REGISTRY.get_sample_value(
        "internet_monitor_upload_failures_total"
    )
    after_upload_total = REGISTRY.get_sample_value("internet_monitor_upload_total")

    assert isinstance(after_upload_duration_seconds_sum, float)
    assert after_upload_failures_total == 1
    assert after_upload_total == 1
