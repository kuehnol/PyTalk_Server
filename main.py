from db import UserDB
from server import Server
from terminal_out import Output

# config, set desired to your needs
PORT: int = 55555
MAX_CONNECTIONS: int = 20

output = Output()
db = UserDB()

if __name__ == "__main__":
    server = Server(output_obj=output, db_obj=db)
    server.start(port=PORT, max_connections=MAX_CONNECTIONS)