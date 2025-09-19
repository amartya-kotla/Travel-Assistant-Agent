# After containerization, it is important to declare the app folder as a package to be used inside the python container.
# For this reason this init.py file exists.

# Takeaways:

# Routes, ports and modules inside a folder need to be explicitly stated to run in a container.

# Environment variables are resolved when running locally by the venv or ide itself. however they need to be explicitly stated in a dockerfile for a container
# Similarly importing modules from a folder requires you to actually package the folder, which is why there is a __init__.py and .before the modules now. This should be standard tho
# We are assigning port 80 to the nginx server in its container, to the port 80 of the computer. so when localhost is accessed, the request is routed to nginx.
# We are proxy passing the request from nginx to the fastapi app service, so the url is not fastaapi_app:8000.

# All are using the greater OS kernel, but are isolated from each other.