# A crude HTTP server

- Crude HTTP server on top of python sockets for experimentation

Requirements:

- Python 3.8.2


Instructions:

- Run server

  ```
  python server.py
  ```


- Open on the browser

	```
	127.0.0.1:8888/index.html
	```

- Or with curl, eg:

	```
	curl 127.0.0.1:8888/index.html -v --http2 
	```