from psycopg2 import sql, errors, connect
import os

class BlogApp_TableNames:
    users = "users"
    likes = "likes"
    posts = "posts"


class BlogApp_DB:
    def __init__(self) -> None:
        self.conn = connect(dbname="BlogApp",
                            user=os.getenv("PostgreUSR"),
                            password=os.getenv("PostgrePWD"),
                            host="localhost"
                            )
        self.cursor = self.conn.cursor()

    def _update_all_occurences(self, data, new_data, column, table):
        try:

            query = sql.SQL("update {} set {} = %s where {} = %s;").format(sql.Identifier(table), sql.Identifier(column),sql.Identifier(column))

            self.cursor.execute(query, (new_data, data))
            self.conn.commit()
        except Exception as e:
            print(e)

    def update_password(self, password, userid):

        query = sql.SQL("update {} set password = %s where userid = %s;").format(sql.Identifier(BlogApp_TableNames.users))
        self.cursor.execute(query, (password, userid))
        self.conn.commit()

    def delete_user(self, userid):
        try:
            query = sql.SQL("delete from {} where userid = %s;").format(sql.Identifier(BlogApp_TableNames.users))
            self.cursor.execute(query, (userid,))
            self.conn.commit()
        except Exception as e:
            print(e)

    def update_username(self, userid, new_username):
        try:
            old_user = self.get_user_by_id(id_=userid)

            self.add_user(username=new_username, password=old_user["password"], profile_picture_src=old_user["profile_picture"])

            self._update_all_occurences(data=old_user["username"],
                                        new_data=new_username,
                                        column="creator",
                                        table="posts")

            self._update_all_occurences(data=old_user["username"],
                                        new_data=new_username,
                                        column="username",
                                        table="likes")

            self.delete_user(userid=userid)

        except Exception as e:
            print(e)

    def add_user(self, username, password, profile_picture_src):
        try:
            query = sql.SQL("insert into {} (username, password, profile_picture) values (%s, %s, %s);").format(sql.Identifier(BlogApp_TableNames.users))
            self.cursor.execute(query, (username, password, profile_picture_src))
            self.conn.commit()
        except errors.UniqueViolation:
            return "Username already exists!"

    def _result_to_dict(self, result):
        # Represent result as dictionary
        desc = self.cursor.description
        column_names = [col[0] for col in desc]
        result = [dict(zip(column_names, row)) for row in result]

        return result

    def create_post(self, creator, title, content):
        query = sql.SQL("insert into {} (creator, title, content) values (%s, %s, %s);").format(sql.Identifier(BlogApp_TableNames.posts))
        self.cursor.execute(query, (creator, title, content))
        self.conn.commit()


    def get_user_by_id(self, id_):
        db_errors = []

        try:
            query = sql.SQL("select * from users where userid = %s limit 1;")
            self.cursor.execute(query, (id_,))
            res = self.cursor.fetchall()
            res = self._result_to_dict(result=res)

            return res[0]
        except Exception as e:
            db_errors.append(e)
            print(db_errors)
            return None

    def delete_like(self, username, postid):
        query = sql.SQL("delete from {} where username like %s and postid = %s").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(query, (username, postid))
        self.conn.commit()

        query = sql.SQL("update posts set {} = likes - 1 where postid = %s;").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(query, (postid,))
        self.conn.commit()

    def add_like(self, username, postid):
        query = sql.SQL("insert into {} (username, postid) values (%s, %s)").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(query, (username, postid))
        self.conn.commit()

        query = sql.SQL("update posts set {} = likes + 1 where postid = %s;").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(query, (postid,))
        self.conn.commit()

    def get_user_likes(self, username: str, limit: int = 100):
        try:
            query = sql.SQL("select (postid) from {} where username like %s limit %s").format(sql.Identifier(BlogApp_TableNames.likes))

            self.cursor.execute(query, (username, limit))
            res = self.cursor.fetchall()

            return res
        except Exception as e:
            print(e)
            return None

    def get_user_posts(self, username: str, limit: int = 100):
        try:
            query = sql.SQL("select * from {} where creator like %s order by postid desc limit %s;").format(sql.Identifier(BlogApp_TableNames.posts))

            self.cursor.execute(query, (username, limit))
            res = self.cursor.fetchall()
            res = self._result_to_dict(result=res)

            return res
        except Exception as e:
            print(e)
            return None

    def get_user(self, username: str):
        db_errors = []

        try:
            query = sql.SQL("select * from users where username like %s limit 1;")
            self.cursor.execute(query, (username,))
            res = self.cursor.fetchall()

            res = self._result_to_dict(result=res)

            return res

        except Exception as e:
            db_errors.append(e)
            print(db_errors)
            return None
