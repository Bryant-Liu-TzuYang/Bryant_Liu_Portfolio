# Bryant Reading

## Nginx

Please explain why this happen: I see the issue! The nginx is trying to connect to http://172.20.0.4:5000 (old backend IP) but the backend container has a new IP 172.20.0.6 after restart.

This happens because Docker assigns dynamic IP addresses to containers on its internal network; when you restart a container, it may get a new IP address.
If your nginx configuration uses a hardcoded backend IP (e.g., http://172.20.0.4:5000), it will break when the backend container's IP changes (e.g., to 172.20.0.6).
The recommended solution is to use Docker service/container names in your nginx config (e.g., http://backend:5000), which Docker DNS will always resolve to the correct container, regardless of its IP.
For more details, see Networking in Compose and NGINX Reverse Proxy to Docker Containers.

## Set bryant as admin

```sh
# First time setup only
docker-compose up -d
# Register bryant98360410@gmail.com via UI
docker-compose exec backend python admin_utils.py --promote bryant98360410@gmail.com admin

# From now on, just regular restarts:
docker-compose restart backend    # Role persists ✅
# or
docker-compose down
docker-compose up                 # Role persists ✅

# Code changes, hot reload, etc. - Role persists ✅
```

Once you promote bryant98360410@gmail.com to admin, that role is stored in the database. The role persists across:

✅ Backend restarts
✅ Code changes
✅ Docker container restarts
✅ Frontend rebuilds
You would need to promote again only if:
You drop/recreate the database (e.g., docker-compose down -v which removes volumes)
You manually delete the user from the database
You reset your development environment completely

## Access SQL CLI inside the container

```sh
docker exec -it voca_recaller_mysql_prod mysql -u root -p
```

The -it flag is actually a combination of two separate flags:

-i (or --interactive): This keeps STDIN (standard input) open even if not attached. It essentially allows you to send input to the container.
-t (or --tty): This allocates a pseudo-TTY (pseudo-terminal). It makes the output look like a regular terminal session (formatted correctly with colors, command prompts, etc.).
Together, -it allows you to interact with the command (like the MySQL shell) as if you were running it directly in your own terminal.

## run the branches at the same time: using the -p flag

```sh
docker compose -p main up -d --build
```
