# Project Details
A multi stage docker build reducing the image size by 86.5% using Docker, python, and Flask. The multi stage docker build is written in a docker file, which docker uses to build a python and Flask REST API image that runs an application. The application has three endpoints: /health, returns 200 OK and a Health message if the container is alive, POST /user, creates a user or returns 409 if a users email already exists, and  DELETE /user/user_id, deletes a user or returns 404 if the user_id is not found.
 
## How to run it
To run image use 'docker run -d -p 5000:5000 aaimarjprojects/flask-api:v2'

### Flags Explained
- -d runs the container in the background so that it does not take up space in my terminal.
- -p 5000: 5000, published port 5000 on the host that forwards any traffic it receives to port 5000 in the container.

## How to use it
I used curl which is a tool that sends http requests. Flags used were -i which shows the response header, -X which specifies the http method, -H which sets the http header and tells Flask the body is json, and -d for the data sent in the request.

### Health Check
curl -i http://<host_ip_address>:5000/health

Expected response: 200 OK and Health message

### Create User
curl -i -X POST -H "Content-Type: application/json" -d '{"name": "<enter_name_here>", "age": <enter_age_here>, "sex": "<enter_sex_here>", "email": <"enter_email_here">}' http://<host_ip_address>:5000/user

Expected response: 200 OK and User created message

### Delete User
curl -i -X DELETE http://<host_ip_address>:5000/user/user_id
 
 Expected response: 200 Ok and User deleted message 

## Reasoning behind the build 
The transition from a single stage build to a multi stage build reduced the image size by 86.5%. 86.5% might just sound like a percentage but it means when the image is pulled it take up 86.5% less space in storage, and every time a container runs using that image it takes up 86.5% less space in memory that it would have taken up in a single stage build. This is done by breaking up the build in the docker file into two steps, step 1 which contain the full python image to use tools like pip and build tools to install the dependencies in requirements.txt file, and step 2 which uses python slim as the base as it only contains the necessary tools to run, reducing the image size, and attack surface then the packages in the filesystem of the build container are copied into the runtime container. 

### Why Flask over plain python with no web framework
Plain python with no web framework means I have to write all the low level network code myself every time for every project. Flask web framework does all this for me so it handles the incoming bytes, parses it, determines which functions handles it, and sends a response back so instead of me writing code to do all that flask does it for me and all I have to do is code the functions.
