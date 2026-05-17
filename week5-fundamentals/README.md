# Week 5 - Docker Fundamentals and Container Theory

## The Problem Containers Solve
When running multiple workloads on one machine without any isolation, two problems emerge. The first is dependency conflicts, if one application needs Python 3.8 and another needs Python 3.11, installing both system wide can break one of them. Libraries and tools installed for one application interfere with another. The second problem is resource starvation since workloads share the same CPU and RAM with nothing stopping one from consuming everything. A greedy or buggy application can eat all available memory, causing other workloads to crash, or consume all CPU, causing everything else to slow to a halt. Containers solve both problems simultaneously as each container gets its own isolated environment and its own resource limits.

## What a Container Actually Is
A container is not a separate computer, it is a regular Linux process that has been isolated and limited using two kernel features. The first is namespaces, which control what the container can see. A PID namespace gives the container its own process numbering so it can only see and kill its own processes, not the host's. A network namespace gives the container its own virtual network interface with its own IP address and ports, completely separate from the host. A mount namespace gives the container its own isolated filesystem view so it cannot read or modify the host's files. The second kernel feature is cgroups, which control what the container can consume, limiting how much CPU, RAM, disk I/O, and network bandwidth it is allowed to use, preventing any one container from starving everything else on the machine.

## Containers vs VMs
A Virtual Machine pretends to be a complete separate computer. It has its own operating system, its own kernel, its own drivers, all simulated in software by a hypervisor like VirtualBox. This gives very strong isolation but it is expensive as each VM needs gigabytes of storage just for its operating system, minutes to boot, and significant RAM just to keep the OS running.

A container shares the host machines kernel. It is a process that the Linux kernel has isolated using namespaces and limited using cgroups. It brings its own filesystem, its own libraries, binaries, and configuration, but not its own kernel. This makes containers much smaller, much faster to start, and far less resource intensive than VMs.

The trade-off is that isolation is less complete. A critical kernel vulnerability on the host could affect all containers, whereas in a VM an attacker would also need to break out of the hypervisor layer. In practice, VMs are used when you need very strong isolation or need to run a completely different operating system. Containers are used when you need to run many workloads quickly and efficiently on the same OS kernel.

Understanding Docker commands requires understanding the container lifecycle, the states a container moves through from creation to deletion.

It starts with an image which is a read only snapshot of a filesystem and configuration, stored on disk until explicitly deleted.`docker pull` downloads an image from Docker Hub without creating anything else. `docker images` lists every image currently on disk.

## Core Commands and Container Lifecycle
`docker stop` sends a SIGTERM signal to the container's main process, giving it time to finish cleanly before stopping. `docker kill` sends SIGKILL immediately with no cleanup time. Either way, the container is now stopped, the writable layer and the read-only image both remain on disk. The container still exists and can be restarted. `docker ps` shows only running containers. `docker ps -a` shows all containers including stopped ones.

`docker rm` removes a stopped container permanently, the writable layer is deleted from disk. The read-only image underneath is completely untouched. Multiple containers can be created from the same image and removing one never affects the others or the image itself.

`docker rmi` removes an image, but only after every container created from that image has been removed first. The cleanup order is always containers first, then images.

## Docker Networking
Docker gives every container a network configuration when it starts. Below are three built-in modes and one critical improvement that should always be used in practice.

**Bridge networking** is the default. Docker creates a virtual network switch and each container gets its own virtual network interface connected to it. Containers on the same bridge network can communicate with each other, but only by IP address, and IP addresses are fragile. If a container restarts it may receive a different IP, silently breaking any connections that depended on it.

**Host networking** removes the network namespace entirely. The container shares the host's network directly, same interfaces, same IP, same ports. If the container listens on port 80 it is occupying port 80 on the host itself. This gives better performance by eliminating NAT translation overhead, but at the cost of complete network isolation. Two containers on host networking fighting for the same port conflict exactly like two processes on the same machine.

**None networking** gives the container a network namespace with nothing in it except a loopback interface. The container cannot send or receive any network traffic whatsoever. This is used for containers that process data with no business touching a network, batch processing, calculations, file transformations. Cutting off network access entirely means even if the container is compromised, it cannot send data out or receive instructions from outside.

**Custom bridge** networks are what you should always use when containers need to communicate reliably. Unlike the default bridge network, Docker enables automatic DNS resolution on user created networks, so containers can reach each other by name rather than by fragile IP address. Docker handles the translation internally. Container A can reach Container B simply by using its name, and the connection survives restarts because the name never changes even if the IP does.
