import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = 2

# 設定 log 輸出到容器內的 logs 資料夾
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

accesslog = os.path.join(log_dir, "gunicorn_access.log")
errorlog = os.path.join(log_dir, "gunicorn_error.log")
loglevel = "info"

# Tell Gunicorn to trust proxy headers from Nginx/Tailscale Serve
forwarded_allow_ips = "*"
proxy_allow_ips = "*"
