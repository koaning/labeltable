import random
from bulk import create_app


def batch_generator():
    """Generates a batch of strings to label."""
    letters = "qwertyuiopasdfghjklzxcvbnm"
    while True:
        strings = ["".join(random.choice(letters) for i in range(5)) for j in range(6)]
        original_id = "".join(random.choice(letters) for i in range(10))
        yield {"original_id": original_id, "items": strings}


gen = batch_generator()

app = create_app(batch_generator=gen)
