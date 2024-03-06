import socket
import threading
import time
from typing import List
from terminal_out import Output
from db import User_DB


class Server():
    def __init__(self, output_obj: Output, db_obj: User_DB) -> None:
        self.__out = output_obj
        self.__db = db_obj

    def __auth_client(self, client_socket: socket.socket) -> str:
        """
        Tries to authenticate client user data with db until authenticated.

        :param client_socket: The client's socket that wants to authenticate.
        :return: The username the client authenticated with.
        """
        db = self.__db

        while True:
            # get operation and user credentials from client
            received_user_data: str = client_socket.recv(1024).decode("utf-8")

            # split user data into its components
            user_data_components = received_user_data.split(":")
            user_operation = user_data_components[0]
            username = user_data_components[1]
            pw_hash = user_data_components[2]

            # do register if client requested so
            if user_operation == "register":
                # if user doesn't already exist in the db
                if not db.user_exists(username):
                    db.add_user(username, pw_hash)
                    self.__out.printout(f'New user "{username}" created.')
                    client_socket.send("OK".encode("utf-8"))
                    break

            # do login if client requested so
            if user_operation == "login":
                # if user has requested login with correct username and password hash
                if db.check_credentials(username, pw_hash) == True:
                    self.__out.printout(f'"{username}" logged in')
                    client_socket.send("OK".encode("utf-8"))
                    break

            # send bad feedback if authentication failed
            client_socket.send("NOT OK".encode("utf-8"))

        return username

    # TODO: Send username & message in one go
    def __broadcast_helper(self, msg: str, sender_socket: socket.socket, clients: List[socket.socket]) -> None:
        """
        Broadcasts messages to every other connected client.

        :param msg: The message to be broadcast.
        :param sender_socket: The client's socket where the message is coming from.
        :param clients: The list containing all connected client sockets.
        """
        # broadcast to all other clients
        for cs in clients:
            # if client is not the client that sent the message
            if cs != sender_socket:
                cs.send(username.encode("utf-8"))
                time.sleep(0.1)
                cs.send(f"{msg}".encode("utf-8"))
                time.sleep(0.1)

    def __handle_client(self, client_socket: socket.socket, clients: list) -> None:
        """
        Handles every connected client seperately.

        param: client_socket: The connected client socket.
        param: clients: The list containing all connected client sockets.
        """
        username = self.__auth_client(client_socket)
        self.__out.printout(f"Successfully authenticated {username}.")

        while True:
            try:
                # receive msg, max 1024 bytes with utf-8 encoding (approx. 1000 chars)
                msg = client_socket.recv(1024).decode("utf-8")

                # if msg empty, break loop
                if msg == "":
                    break

                self.__out.printout(f"Message received, sending to {len(clients) - 1} clients")

                # broadcast message to all other clients
                self.__broadcast_helper(msg, sender_socket=client_socket, clients=clients)

            # if client resets connection, break
            except ConnectionResetError:
                self.__out.printout(f"User {username} reset connection")
                # close connection to client and exit loop
                client_socket.close()
                break
        
        # remove client from client list
        clients.remove(client_socket)

    def __create_client_thread(self, client_socket: socket, clients_list: List[socket.socket]) -> None:
        """
        Create a separate thread to handle communication with an individual client.

        :param client_socket: The connected client socket.
        :param clients_list: The list containing all connected client sockets.
        """
        # initialize client handler thread
        client_handler = threading.Thread(
            target=self.__handle_client, 
            args=(client_socket, clients_list)
        )

        # set as daemon so thread terminates if main thread ends
        client_handler.daemon = True

        # start the client handler thread
        client_handler.start()

    def __connect(self, port: int, max_connections: int) -> socket.socket:
        """
        Create a new server socket and configure it to listen for incoming client connections.

        :param port: The port number where the server will listen for incoming connections.
        :param max_connections: The maximum number of concurrent client connections the server is allowed to handle.
        :return: A connected server socket.
        """
        # create a new socket object using IPv4 and TCP
        s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # allow reuse of the address in case the connection is closed unexpectedly
        s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # bind the listener to specified port on all available network interfaces
        s_sock.bind(("0.0.0.0", port))
        
        # start listening for incoming connections, set maximum allowed connections
        s_sock.listen(max_connections)
        
        return s_sock

    def start(self, port: int, max_connections: int) -> None:
        """
        Start the server by connecting to the given port and accepting incoming client connections.

        :param port: The port number where the server will listen for incoming connections.
        :param max_connections: The maximum number of simultaneous client connections that the server can handle.
        """
        # get server socket
        server_socket = self.__connect(port, max_connections)
        self.__out.printout(f"Server listening on port {port}")

        # store connected client sockets in a list
        client_sockets: List[socket.socket] = []

        try:
            while True:
                # wait for and accept a new client connection
                client_socket, client_address = server_socket.accept()
                self.__out.printout(
                    f"Accepted incoming connection from {client_address[0]}:{client_address[1]}"
                )

                # add the new client socket to the list
                client_sockets.append(client_socket)

                # handle the new client inside a thread
                self.__create_client_thread(client_socket, client_sockets)

        # handle ctrl+c, stop gracefully
        except KeyboardInterrupt:
            self.__out.printout("Closing connection...")

        # close all connected client sockets and server socket
        finally:
            for client_socket in client_sockets:
                client_socket.close()
            server_socket.close()