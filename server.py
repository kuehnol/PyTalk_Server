import socket
import threading
from terminal_out import Output
from db import JSON_db


class Server:
    def __init__(self, port, max_connections):
        self.__port = port
        self.__max_connections = max_connections
        self.__out = Output()

    def __auth_client(self, client_socket):
        db = JSON_db()

        username = client_socket.recv(1024).decode("utf-8")
        pw_hash = client_socket.recv(1024).decode("utf-8")
        
        if username == "" or pw_hash == "":
            return

        auth = db.check_credentials(username, pw_hash)
        if auth == True:
            self.__out.printout(f'"{username}" logged in')
            client_socket.send("OK".encode("utf-8"))
        else:
            db.add_user(username, pw_hash)
            self.__out.printout(f'New user "{username}" created.')
            client_socket.send("OK".encode("utf-8"))

    def __handle_client(self, client_socket, clients):
        self.__auth_client(client_socket)
        while True:
            try:
                # receive msg, max 1024 bytes with utf-8 encoding (approx. 1000 chars)
                msg = client_socket.recv(1024).decode("utf-8")
                # if msg empty, break loop
                if not msg:
                    break

                self.__out.printout(
                    f"Message received, sending to {len(clients) - 1} clients"
                )

                # broadcast to all other clients
                for c in clients:
                    # if client is not the client that sent the message
                    if c != client_socket:
                        c.send(msg.encode("utf-8"))

            # if client resets connection, break
            except ConnectionResetError:
                break

        # close connection to client and remove client from client list
        client_socket.close()
        clients.remove(client_socket)

    def start(self):
        # create socket object, AF_INET: IPv4, SOCK_STREAM: TCP
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind listener to port on all available network interfaces
        server.bind(("0.0.0.0", self.__port))
        # start listener, set max connections to accept
        server.listen(self.__max_connections)

        self.__out.printout(f"Server listening on port {self.__port}")

        # client arr which contains every client for message broadcasting in client_handler()
        clients = []
        
        while True:
            try:
                # if socket accepts client, value for client and addr gets returned by server.accept()
                client, addr = server.accept()
                self.__out.printout(f"New connection: {addr}")
                # append client to clients list
                clients.append(client)

                # start client handler thread
                client_handler = threading.Thread(
                    target=self.__handle_client, args=(client, clients)
                )
                client_handler.start()

            except KeyboardInterrupt:
                self.__out.printout("Closing connection..")
                
                # close all client connections
                for c in clients:
                    print("closed client")
                    c.close()
                
                #close server socket
                server.close()
                print("closed server socket")
                exit()
                break