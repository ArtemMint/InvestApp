from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.crud import get_user_by_email
from app.db.session import get_db
from app.schemas.token import TokenPayload

# Keep OAuth2PasswordBearer to provide OpenAPI metadata (Authorize button in docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/login")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for the given subject (e.g., user email) with an optional expiration time.
    """
    to_encode = {"sub": subject}
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # JWT 'exp' should be a numeric timestamp (UTC)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
        return token_data
    except ExpiredSignatureError:
        # Token explicitly expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"The token is expired\""},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _extract_token_from_request(request: Request) -> Optional[str]:
    """Extract token from cookie 'access_token' (may be 'Bearer <token>') or Authorization header."""
    cookie_val = request.cookies.get('access_token')
    if cookie_val:
        if cookie_val.lower().startswith('bearer '):
            return cookie_val.split(' ', 1)[1]
        return cookie_val

    auth_header = request.headers.get('Authorization') or request.headers.get('authorization')
    if auth_header and auth_header.lower().startswith('bearer '):
        return auth_header.split(' ', 1)[1]

    return None


def is_token_valid(request: Request) -> RedirectResponse | None:
    """Check if the provided token is valid and not expired."""
    token = _extract_token_from_request(request)
    if not token:
        resp = RedirectResponse(url="/login")
        # attempt to clear cookie (HttpOnly) from server side
        resp.delete_cookie('access_token', path='/')
        return resp
    try:
        # decode_access_token will raise HTTPException if the token is invalid or expired
        decode_access_token(token)
    except HTTPException:
        resp = RedirectResponse(url="/login")
        resp.delete_cookie('access_token', path='/')
        return resp


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current user by token from cookie or Authorization header."""
    token = _extract_token_from_request(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token_data = decode_access_token(token)
    user = get_user_by_email(db, email=token_data.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
