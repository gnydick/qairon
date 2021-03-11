#!/usr/bin/env python3

"""
Collects the information about the user's REST requests from the Prometheus.
"""
import math
from datetime import datetime, timedelta
import time
from typing import Optional

import requests
from tabulate import tabulate

# do the port-forward for the Prometheus service
# kubectl -n monitoring port-forward svc/prometheus-operated 9090:9090 &>/dev/null
PROMETHEUS_URL: str = 'http://localhost:9090/'

QUERY_COUNT: str = 'sum(increase(http_server_requests_seconds_count{{uri!~"/actuator/.*",uri!~"/health/.*"}}[{}])) by (service, uri)'
QUERY_MAX: str = 'max_over_time(http_server_requests_seconds_max{{uri!~"/actuator/.*",uri!~"/health/.*"}}[{}])'
QUERY_HISTOGRAM: str = 'histogram_quantile({}, rate(http_server_requests_seconds_bucket{{uri!~"/actuator/.*",uri!~"/health/.*"}}[{}]))'


# period_end: datetime = datetime.now()
# duration: timedelta = timedelta(minutes=60)
period_end = datetime.fromisoformat('2020-11-25T14:08:00')
duration = timedelta(minutes=5)


class UriStats(object):
    def __init__(self, service: str, url: str, count: float):
        self.service: str = service
        self.url: str = url
        self.count: float = count
        self.min: Optional[float] = None
        self.median: Optional[float] = None
        self.p90: Optional[float] = None
        self.p95: Optional[float] = None
        self.p99: Optional[float] = None
        self.p999: Optional[float] = None
        self.max: Optional[float] = None


def query_counters(time_end: datetime, time_duration: str) -> dict:
    response = requests.get(PROMETHEUS_URL + '/api/v1/query', params={
        'query': QUERY_COUNT.format(time_duration),
        'time': time.mktime(time_end.timetuple())
    })
    return response.json()['data']['result']


def query_max(time_end: datetime, time_duration: str) -> dict:
    response = requests.get(PROMETHEUS_URL + '/api/v1/query', params={
        'query': QUERY_MAX.format(time_duration),
        'time': time.mktime(time_end.timetuple())
    })
    return response.json()['data']['result']


def query_histogram(time_end: datetime, time_duration: str, percentile: str) -> dict:
    response = requests.get(PROMETHEUS_URL + '/api/v1/query', params={
        'query': QUERY_HISTOGRAM.format(percentile, time_duration),
        'time': time.mktime(time_end.timetuple())
    })
    return response.json()['data']['result']


def parse_prometheus_response(result: dict) -> tuple[str, str, float]:
    service: str = result['metric']['service']
    url: str = result['metric']['uri']
    value: float = float(result['value'][1])
    return service, url, value


def format_time_metric(value: float) -> str:
    return f'{value:.4f}' if value else '-'


time_range: str = str(duration.seconds) + 's'
results_count = query_counters(period_end, time_range)
results_histogram_median = query_histogram(period_end, time_range, '0.5')
results_histogram_90 = query_histogram(period_end, time_range, '0.9')
results_histogram_95 = query_histogram(period_end, time_range, '0.95')
results_histogram_99 = query_histogram(period_end, time_range, '0.99')
results_histogram_999 = query_histogram(period_end, time_range, '0.999')
results_max = query_max(period_end, time_range)

# parse the response in to the list
stats: dict[str, dict[str, UriStats]] = {}
for result in results_count:
    service, url, counter = parse_prometheus_response(result)
    if counter == 0:
        continue

    if service not in stats:
        stats[service] = {}
    stats[service][url] = UriStats(service, url, counter)

for result in results_histogram_median:
    service, url, value = parse_prometheus_response(result)
    if value == 0 or math.isnan(value):
        continue
    if service not in stats:
        stats[service] = {}
    if url not in stats[service]:
        stats[service][url] = UriStats(service, url, 0)
    stats[service][url].median = value

for result in results_histogram_90:
    service, url, value = parse_prometheus_response(result)
    if value == 0 or math.isnan(value):
        continue
    if service not in stats:
        stats[service] = {}
    if url not in stats[service]:
        stats[service][url] = UriStats(service, url, 0)
    stats[service][url].p90 = value

for result in results_histogram_95:
    service, url, value = parse_prometheus_response(result)
    if value == 0 or math.isnan(value):
        continue
    if service not in stats:
        stats[service] = {}
    if url not in stats[service]:
        stats[service][url] = UriStats(service, url, 0)
    stats[service][url].p95 = value

for result in results_histogram_99:
    service, url, value = parse_prometheus_response(result)
    if value == 0 or math.isnan(value):
        continue
    if service not in stats:
        stats[service] = {}
    if url not in stats[service]:
        stats[service][url] = UriStats(service, url, 0)
    stats[service][url].p99 = value

for result in results_histogram_999:
    service, url, value = parse_prometheus_response(result)
    if value == 0 or math.isnan(value):
        continue
    if service not in stats:
        stats[service] = {}
    if url not in stats[service]:
        stats[service][url] = UriStats(service, url, 0)
    stats[service][url].p999 = value

for result in results_max:
    service, url, value = parse_prometheus_response(result)
    if value == 0 or math.isnan(value):
        continue
    if service not in stats or url not in stats[service]:
        continue
    stats[service][url].max = value


# print the output
print(f'# Measurement duration: {duration}')
print('# RPS - requests per second')
print('# time in the table is in the seconds')
print("{:>6} {:>6} | {:>7} {:>7} {:>7} {:>7} {:>7} {:>7}   {:<50}".format('Total', 'RPS', 'median', '90p', '95p', '99p', '99.9p', 'max', 'URL'))

for service, urls in sorted(stats.items()):
    print(f'-- {service} --')
    for url, stat in sorted(urls.items()):
        print("{:>6} {:>6} | {:>7} {:>7} {:>7} {:>7} {:>7} {:>7}   {:<50}".format(
            f'{stat.count:.0f}',
            f'{stat.count / duration.seconds:.1f}',
            format_time_metric(stat.median),
            format_time_metric(stat.p90),
            format_time_metric(stat.p95),
            format_time_metric(stat.p99),
            format_time_metric(stat.p999),
            format_time_metric(stat.max),
            url
        ))
