from psycopg2 import sql, errors


class BlogApp_TableNames:
    users = "users"
    likes = "likes"
    posts = "posts"


class BlogApp_DB:
    def __init__(self, conn) -> None:
        self.conn = conn
        self.cursor = conn.cursor()

    def add_user(self, username, password):
        try:
            request = sql.SQL("insert into {} (username, password) values (%s, %s);").format(sql.Identifier(BlogApp_TableNames.users))
            self.cursor.execute(request, (username, password))
            self.conn.commit()
        except errors.UniqueViolation:
            return "Username already exists!"

        return None

    def _result_to_dict(self, result):
        # Represent result as dictionary
        desc = self.cursor.description
        column_names = [col[0] for col in desc]
        result = [dict(zip(column_names, row)) for row in result]

        return result

    def create_post(self, creator, title, content):
        request = sql.SQL("insert into {} (creator, title, content) values (%s, %s, %s);").format(sql.Identifier(BlogApp_TableNames.posts))
        self.cursor.execute(request, (creator, title, content))
        self.conn.commit()


    def get_user_by_id(self, id_):
        db_errors = []

        try:
            request = sql.SQL("select * from users where userid = %s limit 1;")
            self.cursor.execute(request, (id_,))
            res = self.cursor.fetchall()
            res = self._result_to_dict(result=res)

            return res[0]
        except Exception as e:
            db_errors.append(e)
            print(db_errors)
            return None

    def delete_like(self, username, postid):
        request = sql.SQL("delete from {} where username like %s and postid = %s").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(request, (username, postid))
        self.conn.commit()

        request = sql.SQL("update posts set {} = likes - 1 where postid = %s;").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(request, (postid,))
        self.conn.commit()

    def add_like(self, username, postid):
        request = sql.SQL("insert into {} (username, postid) values (%s, %s)").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(request, (username, postid))
        self.conn.commit()

        request = sql.SQL("update posts set {} = likes + 1 where postid = %s;").format(sql.Identifier(BlogApp_TableNames.likes))

        self.cursor.execute(request, (postid,))
        self.conn.commit()

    def get_user_likes(self, username: str, limit: int = 100):
        try:
            request = sql.SQL("select (postid) from {} where username like %s limit %s").format(sql.Identifier(BlogApp_TableNames.likes))

            self.cursor.execute(request, (username, limit))
            res = self.cursor.fetchall()
            #res = self._result_to_dict(result=res)

            return res
        except Exception as e:
            print(e)
            return None

    def get_user_posts(self, username: str, limit: int = 100):
        try:
            request = sql.SQL("select * from {} where creator like %s order by postid desc limit %s;").format(sql.Identifier(BlogApp_TableNames.posts))

            self.cursor.execute(request, (username, limit))
            res = self.cursor.fetchall()
            res = self._result_to_dict(result=res)

            return res
        except Exception as e:
            print(e)
            return None

    def get_user(self, username: str):
        db_errors = []

        try:
            request = sql.SQL("select * from users where username like %s limit 1;")
            self.cursor.execute(request, (username,))
            res = self.cursor.fetchall()

            res = self._result_to_dict(result=res)

            return res

        except Exception as e:
            db_errors.append(e)
            print(db_errors)
            return None
