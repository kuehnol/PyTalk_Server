import socket
import threading
import time # TODO: remove later
from terminal_out import Output
from db import JSON_db


class Server:
    def __init__(self, port, max_connections):
        self.__port = port
        self.__max_connections = max_connections
        self.__out = Output()

    def __auth_client(self, client_socket):
        # create db object
        db = JSON_db()
        
        # get username and password hash from client
        username = client_socket.recv(1024).decode("utf-8")
        pw_hash = client_socket.recv(1024).decode("utf-8")
        
        # check if empty
        if username == "" or pw_hash == "":
            return

        # TODO: do something about spaces as last username char
        # check if user logs in with correct credentials
        auth = db.check_credentials(username, pw_hash)
        if auth == True:
            self.__out.printout(f'"{username}" logged in')
            client_socket.send("OK".encode("utf-8"))
        # else create an account, TODO: check for username already existing before creating account
        else:
            db.add_user(username, pw_hash)
            self.__out.printout(f'New user "{username}" created.')
            client_socket.send("OK".encode("utf-8"))
        return username

    def __handle_client(self, client_socket, clients):
        username = self.__auth_client(client_socket)
        client_active = True
        while client_active:
            try:
                # receive msg, max 1024 bytes with utf-8 encoding (approx. 1000 chars)
                msg = f'{username}: {client_socket.recv(1024).decode("utf-8")}'
                # if msg empty, break loop
                if msg == "":
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
            clients.remove(client_socket)
            client_socket.close()

    def start(self):
        # create socket object, AF_INET: IPv4, SOCK_STREAM: TCP
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind listener to port on all available network interfaces
        server.bind(("0.0.0.0", self.__port))
        # start listener, set max connections to accept
        server.listen(self.__max_connections)

        self.__out.printout(f"Server listening on port {self.__port}")

        # client arr which contains every client for message broadcasting in client_handler()
        clients = []
        
        try:
            while True:
                # if socket accepts client, value for client and addr gets returned by server.accept()
                client, addr = server.accept()
                self.__out.printout(f"Accepted incoming connection from {addr[0]}:{addr[1]}")
                
                # append client to clients list
                clients.append(client)

                # start client handler thread
                client_handler = threading.Thread(
                    target=self.__handle_client, args=(client, clients)
                )
                client_handler.daemon = True
                client_handler.start()
                
        # stop server properly on ^C, close connections
        except KeyboardInterrupt:
            self.__out.printout("Closing connection...")
        finally:
            for c in clients:
                c.close()
            server.close()