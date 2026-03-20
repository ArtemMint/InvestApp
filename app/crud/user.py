"""
CRUD operations for users.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core import get_password_hash, verify_password
from app.models import User
from app.schemas import UserRegister
from app.utils.helpers import timing


@timing
def get_user_by_email(db: Session, *, email: str) -> Optional[User]:
    """
    Retrieve a user by their email address.

    :param db: database session
    :param email: email address to search for
    :return: User object if found, else None
    """
    return db.query(User).filter(User.email == email).first()


@timing
def create_user(db: Session, *, user_in: UserRegister) -> User:
    """
    Create a new user with hashed password.

    :param db: database session
    :param user_in: UserRegister object containing email and password
    :return: Created User object with hashed password
    """
    hashed = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, password_hash=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@timing
def update_user_password(db: Session, *, user: User, new_password: str) -> User:
    """
    Update a user's password by hashing the new password and saving it to the database.

    :param db: database session
    :param user: User object whose password is to be updated
    :param new_password: new password in plain text to be hashed and stored
    :return: Updated User object with the new password hash
    """
    user.password_hash = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@timing
def delete_user(db: Session, *, email: str) -> User | None:
    """
    Delete a user from the database.

    :param db: database session
    :param user: User object to be deleted
    :return: Deleted User object
    """
    if user := get_user_by_email(db, email=email):
        db.delete(user)
        db.commit()
        return user
    return None


@timing
def authenticate_user(db: Session, user_in) -> Optional[User]:
    """
    Accept either:
    - pydantic model with .username/.email and .password (OAuth2PasswordRequestForm gives .username)
    - UserLogin with .email and .password

    :param db: database session
    :param user_in: input object containing login credentials
    :return: Authenticated User object if credentials are valid, else None
    """
    # Handle OAuth2PasswordRequestForm
    username = getattr(user_in, "username", None)
    email = getattr(user_in, "email", None)
    password = getattr(user_in, "password", None)

    login_email = username if username else email
    if not login_email or not password:
        return None

    user = get_user_by_email(db, email=login_email)
    if not user:
        # perform dummy verify inside verify_password if configured to mitigate timing
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
