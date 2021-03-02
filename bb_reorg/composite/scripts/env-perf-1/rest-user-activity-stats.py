#!/usr/bin/env python3

"""
Collects the information about the user's REST requests from the Prometheus.
"""
from datetime import datetime, timedelta
import time
import requests

# do the port-forward for the Prometheus service
# kubectl -n monitoring port-forward svc/prometheus-operated 9090:9090 &>/dev/null
PROMETHEUS_URL: str = 'http://localhost:9090/'

period_end: datetime = datetime.now()
duration: timedelta = timedelta(minutes=15)

# int-2:  2020-11-17T14:08:00 - 2020-11-17T14:28:00, average online: 9
# period_end = datetime.fromisoformat('2020-11-17T14:28:00')
# duration = timedelta(minutes=20)

# prod-1: 2020-11-18T01:30:00 - 2020-11-18T03:00:00, average online: 6
# period_end = datetime.fromisoformat('2020-11-18T03:00:00')
# duration = timedelta(minutes=90)


time_range: str = str(duration.seconds) + 's'
response = requests.get(PROMETHEUS_URL + '/api/v1/query', params={
  'query': f'sum(rate(http_server_requests_seconds_count{{uri!~"/actuator/.*",uri!~"/health/.*"}}[{time_range}]) * 60) by (service, uri)',
  'time': time.mktime(period_end.timetuple())
})
results = response.json()['data']['result']

# parse the response in to the dictionary
# {service: {url: counter} }
counters: dict[str, dict[str, float]] = {}
for result in results:
    counter: float = float(result['value'][1])
    if counter == 0:
        continue
    service: str = result['metric']['service']
    url: str = result['metric']['uri']
    if service in counters:
        counters[service][url] = counter
    else:
        counters[service] = {url: counter}

# print the output
print('# output: URL -> requests per minute')
for service, urls in sorted(counters.items()):
    print(service)
    for url, counter in urls.items():
        print(f'  {url}: {counter:.2f}')
