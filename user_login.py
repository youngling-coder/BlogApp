from flask_login import UserMixin


class UserLogin(UserMixin):
    def __init__(self) -> None:
        super().__init__()

    def login(self, user):
        self.__user = user
        return self

    def logout(self):
        self.__user = None

    def from_db(self, user_id, db):
        self.__user = db.get_user_by_id(user_id)
        return self

    def get_id(self):
        return str(self.__user['userid'])

    def get_username(self):
        return str(self.__user['username'])
