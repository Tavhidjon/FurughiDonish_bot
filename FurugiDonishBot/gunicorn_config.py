# gunicorn_config.py
bind = "0.0.0.0:8080"
workers = 2
threads = 4
timeout = 120
accesslog = "-"
errorlog = "-"
capture_output = True
worker_class = "gthread"
