Please explain why this happen: I see the issue! The nginx is trying to connect to http://172.20.0.4:5000 (old backend IP) but the backend container has a new IP 172.20.0.6 after restart.

This happens because Docker assigns dynamic IP addresses to containers on its internal network; when you restart a container, it may get a new IP address.
If your nginx configuration uses a hardcoded backend IP (e.g., http://172.20.0.4:5000), it will break when the backend container's IP changes (e.g., to 172.20.0.6).
The recommended solution is to use Docker service/container names in your nginx config (e.g., http://backend:5000), which Docker DNS will always resolve to the correct container, regardless of its IP.
For more details, see Networking in Compose and NGINX Reverse Proxy to Docker Containers.