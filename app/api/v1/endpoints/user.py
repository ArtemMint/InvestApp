from datetime import timedelta

from fastapi import HTTPException, APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user
from app.crud import get_user_by_email, create_user, authenticate_user, update_user_password
from app.crud.user import delete_user
from app.db.session import get_db
from app.schemas import UserResponse, UserRegister, UserUpdate
from app.utils.helpers import log_request

router = APIRouter()


@log_request
@router.get("/{email}", response_model=UserResponse, status_code=200)
async def get_user(
        email: str,
        db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get a user by email. Raises HTTPException if the user is not found.

    :param email: user's email
    :param db: database session
    :return: User information. Raises HTTPException if user is not found.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@log_request
@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
        email: str,
        password: str,
        db: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user with the given email and password hash.
    Raises HTTPException if the email is already registered.

    :param email: user's email
    :param password: user's password (will be hashed)
    :param db: database session
    :return: Created user information. Raises HTTPException if email is already registered.
    """
    existing_user = get_user_by_email(db, email=email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_user(db, user_in=UserRegister(email=email, password=password))
    return UserResponse.model_validate(new_user)


@log_request
@router.put("/password", response_model=UserResponse, status_code=200)
async def change_password(
        user_update: UserUpdate,
        db: Session = Depends(get_db)
) -> UserResponse:
    """
    Change a user's password. Raises HTTPException if the user is not found.

    :param user_update: UserUpdate object containing email and new password
    :param db: database session
    :return: Updated user information. Raises HTTPException if user is not found.
    """
    user = get_user_by_email(db, email=user_update.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_user_password(db, user=user, new_password=user_update.password)
    return UserResponse.model_validate(updated_user)


@log_request
@router.post("/login", status_code=200)
async def login_user(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> dict:
    """
    Authenticate user and return an access token for UI login. Accepts form data with .email and .password.

    :param response: FastAPI Response object to set cookies
    :param form_data: OAuth2PasswordRequestForm with .email and .password
    :param db: database session
    :return: JSON with access_token, token_type, and user info. Raises HTTPException if authentication fails.
    """
    user = authenticate_user(db, user_in=form_data)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(subject=user.email, expires_delta=timedelta(minutes=60))
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,  # Only send cookie over HTTPS
        samesite="lax"
    )
    # return token + user info
    return {"access_token": access_token, "token_type": "bearer", "user": UserResponse.model_validate(user)}


@log_request
@router.post("/logout", status_code=200)
async def logout_user(response: Response) -> dict:
    """
    Logout user by clearing the 'access_token' cookie. Frontend should call this (with credentials included)
    to remove the HttpOnly cookie set at login.
    """
    # instruct browser to delete cookie
    response.delete_cookie(key="access_token", path="/")
    return {"msg": "logged out"}


@log_request
@router.delete("/{email}", status_code=204)
async def remove_user(
        email: str,
        db: Session = Depends(get_db)
) -> Response:
    """
    Delete a user by email. Raises HTTPException if the user is not found.

    :param email: user's email
    :param db: database session
    :return: None. Raises HTTPException if user is not found.
    """
    delete_user(db, email=email)
    return Response(status_code=204)


@log_request
@router.get("/me", response_model=UserResponse, status_code=200)
async def read_current_user(
        current_user=Depends(get_current_user)
) -> UserResponse:
    """
    Get the currently authenticated user's information. Requires a valid access token.

    :param current_user: Injected by get_current_user dependency, which retrieves user info from the access token.
                         Raises HTTPException if not authenticated.
    :return: Current user's information. Raises HTTPException if user is not authenticated.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UserResponse.model_validate(current_user)
