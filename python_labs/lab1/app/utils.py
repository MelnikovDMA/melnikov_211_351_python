import random
from faker import Faker

fake = Faker()

def get_random_comments(replies):
    comments = []
    for i in range(random.randint(1, 3)):
            comment = { 'author': fake.name(), 'text': fake.text() }
            if replies:
                comment['replies'] = get_random_comments(replies=False)
            comments.append(comment)
    return comments