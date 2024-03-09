import json


class UserDB:
    def __init__(self):
        self.__json_file = "user_db.json"

    def __read_db(self) -> dict:
        """
        Opens and reads json user database.

        :return: Returns db contents.
        """
        # open json db and load contents into user_db
        with open(self.__json_file, "r") as db_file:
            user_db = json.load(db_file)

        return user_db

    def add_user(self, new_username: str, new_pw_hash: str) -> None:
        """
        Writes a new user to the database.

        :param new_username: Username to be written.
        :param new_pw_hash: Password hash to be written.
        """
        user_db = self.__read_db()
        new_user = {"username": new_username, "pw_hash": new_pw_hash}
        user_db[new_username] = new_user

        # write changes to file
        with open(self.__json_file, "w") as db_file:
            json.dump(user_db, db_file, indent=4)

    def user_exists(self, username: str) -> bool:
        """
        Checks if username is in db.

        :param username: The username to be checked.
        :return: Username exists or does not exist
        """
        user_db = self.__read_db()

        return username in user_db

    def check_credentials(self, username: str, pw_hash_attempt: str) -> bool:
        """
        Checks username and password hash against db.

        :param username: The username to be checked.
        :param pw_hash_attempt: The password hash to be checked.
        :return: Auth successful or unsuccessful
        """
        user_db = self.__read_db()

        if not self.user_exists(username):
            return False
        
        return user_db[username]["pw_hash"] == pw_hash_attempt
