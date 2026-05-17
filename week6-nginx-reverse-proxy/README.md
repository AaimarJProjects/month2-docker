# Week 6 - Nginx Containers, Docker Networking and Reverse Proxy

## What This Week Built

Built a multi-container reverse proxy architecture using Docker and Nginx. A single reverse proxy container acts as the public entry point, routing traffic to two isolated backend containers by URL path, the backends are unreachable directly from outside, making the entire system appear as one server to the client.

## Architecture



## How the Request Path Works

When a browser requests `http://<ubuntu-ip>:8080/backend1/`, the request arrives at the host on port 8080. Docker's port mapping translates it and forwards it into the reverseproxy container on port 80. Nginx inside the reverseproxy reads the HTTP header, matches the path `/backend1/` against its configured location blocks, and forwards the request to the container named backend1 using `proxy_pass`. Docker DNS resolves the name backend1 to its IP address on proxynetwork. The backend1 container receives the request, finds the index.html file at `/usr/share/nginx/html`, and sends the response back to the reverseproxy. The reverseproxy passes the response back out through Docker's port mapping to the host, which returns it to the browser. The browser never communicates directly with backend1 at any point.

## Nginx Reverse Proxy Config

```nginx
server {
    listen 80;

    location /backend1/ {
        proxy_pass http://backend1/;
    }

    location /backend2/ {
        proxy_pass http://backend2/;
    }
}
```

The `server` block defines a virtual server inside Nginx. Everything inside it applies to requests this server receives.

`listen 80` tells Nginx to listen for incoming requests on port 80 inside the container's network namespace. This port is not directly reachable from outside because the `-p 8080:80` flag in the docker run command connects the host's port 8080 to this internal port 80 via Docker's NAT translation.

Each `location` block matches incoming requests by URL path. When a request arrives for `/backend1/`, the first block matches it. When a request arrives for `/backend2/`, the second block matches it.

`proxy_pass http://backend1/` forwards the matched request to the container named backend1. Docker DNS on the custom bridge network resolves the name backend1 to its actual IP address internally, no hardcoded IPs needed. This is why a custom bridge network is required because the default bridge network does not support name resolution.

## Docker Compose File

```yaml
services:
  backend1:
    image: nginx
    networks:
      - proxynetwork
    volumes:
      - ./backend1:/usr/share/nginx/html

  backend2:
    image: nginx
    networks:
      - proxynetwork
    volumes:
      - ./backend2:/usr/share/nginx/html

  reverseproxy:
    image: nginx
    networks:
      - proxynetwork
    ports:
      - "8080:80"
    volumes:
      - ./default.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend1
      - backend2

networks:
  proxynetwork:
    driver: bridge
```

Docker Compose describes the entire multi-container architecture in a single file. Each entry under `services` defines one container, its image, network, ports, and bind mounts.

`image: nginx` tells Compose to pull the official Nginx image from Docker Hub rather than building a custom one.

`networks` connects each service to proxynetwork. All three containers share this network, which is what allows the reverseproxy to reach backend1 and backend2 by name using Docker DNS.

`volumes` defines the bind mounts. For backend1 and backend2, `./backend1:/usr/share/nginx/html` mounts the local backend1 folder into the path where Nginx looks for files to serve, replacing the default welcome page with custom content. The `./` means the path is relative to where the Compose file lives, making the project portable across any machine. For reverseproxy, the custom `default.conf` is mounted directly over the default Nginx config file, turning it from a plain web server into a reverse proxy.

`ports` only appears on reverseproxy as `8080:80` publishes the host's port 8080 into the container's port 80. backend1 and backend2 have no port publishing deliberately because they are internal services unreachable from outside the network.

`depends_on` ensures backend1 and backend2 start before reverseproxy. Without this, reverseproxy could start first and attempt to resolve container names that do not exist yet.

The `networks` block at the bottom defines and configures proxynetwork itself as a custom bridge network. The network references inside each service connect them to this already defined network, defining and joining are two separate things in Compose.

## Key Decisions and Why

**Why backend containers have no port publishing ?**

Backend containers are internal services that should never be reachable directly from outside the network. The reverse proxy is the single public entry point, all traffic must pass through it so routing rules, logging, and security controls are applied consistently. Exposing backends directly would bypass all of that.

**Why a custom bridge network instead of the default ?**

The default bridge network only supports container to container communication by IP address, which changes every time a container restarts. A custom bridge network enables Docker's automatic DNS resolution so containers can reach each other by name. The name never changes even if the IP does, meaning connections survive restarts without breaking.

**Why `nginx -s reload` is preferred over a full container restart ?**

A full container restart stops the container completely, dropping all active connections for that moment. `nginx -s reload` sends a reload signal to the Nginx master process inside the running container, it reads the new configuration and hands it off to new worker processes while the old workers finish serving any in-flight requests. Zero downtime, no connections dropped. In production this distinction matters significantly.
