# Internet Provider Monitor

## What

This is a personal project with a simple goal of monitoring my internet provider performance: lantency and download/upload speed. Also, it is an opportunity to connect multiple technologies together and deliver an observability framework comprising of alerting, monitoring and logging (tracing will come later).

## Why

Of course you could run any speed test, or ping to detect if you network is down, but how fun is it? Also, I wanted to have historical data to see how good/bad my provider is.

## How

A few components were used:

- Python Job Scheduler, instrumented with Prometheus metrics, that triggers jobs to test ICMP echo request latency average RTT, download/upload performance
- Prometheus /metrics is added to the code and a few custom metrics to track latency, and download/upload speed (MB/s)
- Prometheus server using a container is used to pull the data
- Grafana is used to present the data and show the past
- Python standard logging with details about the job execution and the overall app messages
- Docker and docker-compose is used to build and run the monitor app, prometheus, grafana and the alert manager
- Flake8 to check for pep8 issues
- cAdvisor exposes container information such as memory/cpu consumption for all containers running under docker-compose control
- Loki to show logs in grafana
- Node exporter to gather node metrics
- Alertmanager to manager alerts sent from prometheus

## Tech stack

- Python 3
- Docker
- docker-compose
- prometheus
- alertmanager
- grafana
- flake8
- cAdvisor
- GNU Make
- node-exporter
- loki

## Running the code

### Pre-requisites

- A working docker and docker-compose
- Git to download the code

### How to run

```bash
git clone https://github.com/global/internet-monitor.git
make init
make build
make run
make urls
```

Open:

- http://localhost:9090/ - to access prometheus
- http://localhost:3000/ - to access grafana (login: admin / pass: admin)
  - There is a pre-configured dashboard called `Internet Monitoring`. When logged in, click to access the information
  - To visualize all the data, wait about 5 min, as this is the time the download speed job kicks in
- http://localhost:8000/metrics - to access the internet-monitor metrics
- http://localhost:8080/ - to access cAdvisor (you can also access the metrics through prometheus and grafana)

This is the `Internet Monitoring` you will get when opening grafana:

![Grafana Internet Monitor Dashboard](docs/grafana.png "Grafana Internet Monitor Dashboard")

## Development

## Bugs and Known Issues

- Sometimes my docker for mac stop accepting inbound ICMP traffic and I need to restart it to get my `ping` working again

## TODO

- Understand the impact of low start to the download/upload calculation (it is good enough for now, but we could do better)
  - I still don't understand it fully, but I think the [RFC1323](https://tools.ietf.org/html/rfc1323) will help me
- Create a demo video
- Integrate our alerthook with alertmanager
- Deploy into kubernetes
- Add container resources dashboard into grafana