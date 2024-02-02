from server import Server

# config
port = 55555
max_connections = 20

# max_connections needs testing for recommended value,
# 100s or even 1000s of concurrent connections might be managable

# start server
server = Server(port, max_connections)
server.start()
