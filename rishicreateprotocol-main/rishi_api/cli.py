# CLI command to add a user
import click
from models import User
from database import SessionLocal, engine, Base
from utils import get_password_hash

@click.command()
@click.option('--username', prompt=True, help='The username of the new user')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password for the new user')
def add_user(username, password):
    db = SessionLocal()
    hashed_password = get_password_hash(password)
    print(hashed_password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    click.echo(f"User {username} added successfully.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    add_user()

    insert into users(username,hashed_password) values('admin','$2b$12$zBsEU5ZHNYTHI8sbLI3heevZuIu5DUiCUzFiN8vNX6ukcTqWObf6e');
