import multiprocessing
bind = "0.0.0.0:5001"
worker_class = 'sync'
workers = 1  # multiprocessing.cpu_count() * 2 + 1
wsgi_app = "app:app"
reload = True
logger_class = 'gunicorn.glogging.Logger'
timeout = 9999
keepalive = 9999

def pre_request(worker, req):
    req.headers.append(tuple(['X-FORWARDED-PROTO', 'https']))
    for header in req.headers:
        worker.log.info(header)
