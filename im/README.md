# Internet Monitor

This application monitors yours internet speed and latency, by scheduling ICMP
requests and HTTP requests (download/upload).

It also generates the following prometheus-style metrics:

- **ICMP metrics**
  - internet_monitor_ping_total (counter): Total ping requests made to 1.1.1.1
  - internet_monitor_ping_failures_total (counter): Total ping requests failed made to 1.1.1.1
  - internet_monitor_ping_packet_loss_total (counter): Number of packets lost while checking latency
  - internet_monitor_ping_jitter_seconds (guage): ICMP Jitter
  - internet_monitor_up (gauge): Internet is up or down
  - internet_monitor_ping_latency_seconds (summary): Ping latency to 1.1.1.1

- Download metrics
  - internet_monitor_download_duration_seconds (histogram): Download latency - buckets=(1, 2, 5, 7, 10, 15, 20, 50, 100, INF)
  - internet_monitor_download_size_bytes (gauge): Bytes downloaded
  - internet_monitor_download_total (counter): Number of times the download job runs
  - internet_monitor_download_failures_total (counter): Number of times the download job fails

- Upload metrics
  - internet_monitor_upload_duration_seconds (histogram): Upload latency - buckets=(1, 2, 5, 7, 10, 15, 20, 50, 100, INF)
  - internet_monitor_upload_total (counter): Number of times the upload job runs
  - internet_monitor_upload_failures_total (counter): Number of times the upload job fails
  - internet_monitor_upload_size_bytes (gauge): Bytes uploaded
