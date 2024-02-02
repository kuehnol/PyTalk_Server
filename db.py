import json


class JSON_db:
    def __init__(self):
        self.__json_file = "user_db.json"

    def __read_db(self):
        # open json db and load contents into user_db
        with open(self.__json_file, "r") as json_db:
            user_db = json.load(json_db)
            
        json_db.close()
        return user_db

    def add_user(self, new_username, new_pw_hash):
        # get db data
        user_db = self.__read_db()
        
        # create user entry in json format
        new_user = {"username": new_username, "pw_hash": new_pw_hash}
        # add to user_db
        user_db[new_username] = new_user

        # write changes to file
        with open(self.__json_file, "w") as json_db:
            json.dump(user_db, json_db, indent=4)
            
        json_db.close()

    def check_credentials(self, username, pw_hash_attempt):
        # set authentication status to false
        auth = False
        
        # get db data
        user_db = self.__read_db()

        # if username in db, return true, else it stays at false
        if username in user_db: # to remove, maybe, idk?
            if user_db[username]["pw_hash"] == pw_hash_attempt:
                auth = True
        return auth
