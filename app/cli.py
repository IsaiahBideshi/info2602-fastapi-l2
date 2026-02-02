import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from typing import Annotated

cli = typer.Typer()

@cli.command()
def initialize():
    """
    Initializes the database by creating tables and adding a default user
    """
    
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables

        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        
        print("Database Initialized")

@cli.command()
def get_user(username: Annotated[str, typer.Argument(help="Username of the user to retrieve")]):
    """
    Finds a user given their username and displays their information
    """

    with get_session() as db: # Get a connection to the database
            user = db.exec(select(User).where(User.username == username)).first()
            if not user:
                print(f'{username} not found!')
                return
            print(user)

@cli.command()
def get_all_users():
    """
    Shows all users in the database
    """
    with get_session() as db:
        users = db.exec(select(User)).all()
        if not users:
            print("Error: No Users Found!")

        for user in users:
            print(user)


@cli.command()
def change_email(username: Annotated[str, typer.Argument(help="Username of the user to change email")], new_email: Annotated[str, typer.Argument(help="New email address")]):
    """
    Changes the email of a user given their username
    """    
    
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        
        if not user:
            print("Error: User not found!")
            return

        user.email = new_email
        db.add(user)
        db.commit()
        db.refresh(user)

        print("Successfully changed email!")

@cli.command()
def create_user(username: Annotated[str, typer.Argument(help="Username of the new user")], email: Annotated[str, typer.Argument(help="Email of the new user")], password: Annotated[str, typer.Argument(help="Password of the new user")]):
    """
    Creates a new user with the given username, email, and password
    """    
    
    with get_session() as db:
        newUser = User(username, email, password)
        try:
            db.add(newUser)
            db.commit()
        except :
            print("Error: User already exists!")
            return
        
        print(f"Successfully added user {username}")

@cli.command()
def delete_user(username: Annotated[str, typer.Argument(help="Username of the user to delete")]):
    """
    Deletes a user given their username
    """

    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()

        if not user:
            print("User not found!")
            return

        db.delete(user)
        db.commit()

        print("Succesfully deleted user!")

@cli.command()
def search_user(query: Annotated[str, typer.Argument(help="Search query for username or email")]):
    """
    Searches for a user by username or email
    """


    with get_session() as db:
        if '@' in query:
            print("Searching for email")
            users = db.exec(select(User)).all()

            for user in users:
                if query in user.email:
                    print(f"Match found! {user.email}")
                    return
            
        else:
            print("Searching for username")
            users = db.exec(select(User)).all()

            for user in users:
                if query in user.username:
                    print(f"Match found! {user.username}")
                    return
        
        print("User not found!")



@cli.command()
def list_users(limit: Annotated[int, typer.Argument(help="Amount of users per page")] = 10, offset: Annotated[int, typer.Argument(help="Offset for pagination")] = 0,):     # 'Annotated[]' got from link in lab 
    """
    Lists users with pagination
    """

    with get_session() as db:
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        for user in users:
            print(user)

if __name__ == "__main__":
    cli()