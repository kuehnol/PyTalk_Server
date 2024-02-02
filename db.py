import json


class JSON_db:
    def __init__(self):
        self.__json_file = "user_db.json"

    def __read_db(self):
        with open(self.__json_file, "r") as json_db:
            user_db = json.load(json_db)
        json_db.close()
        return user_db

    def add_user(self, new_username, new_pw_hash):
        user_db = self.__read_db()
        new_user = {"username": new_username, "pw_hash": new_pw_hash}
        user_db[new_username] = new_user

        with open(self.__json_file, "w") as json_db:
            json.dump(user_db, json_db, indent=4)
        json_db.close()

    def check_credentials(self, username, pw_hash_attempt):
        auth = False
        user_db = self.__read_db()

        if username in user_db:
            if user_db[username]["pw_hash"] == pw_hash_attempt:
                auth = True
        return auth
