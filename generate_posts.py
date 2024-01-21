from db import BlogApp_DB
import random
from faker import Faker

fk = Faker()


def _generate_title():
    return fk.sentence()

def _generate_content():
    return "".join(fk.paragraph() for i in range(random.randint(3, 9)))

def generate_posts(username: str):
    db_ = BlogApp_DB()

    for i in range(random.randint(3, 9)):
        title = _generate_title()
        content = _generate_content()

        db_.create_post(creator=username, title=title, content=content)
