from fastapi import HTTPException, status


class SomethingWentWrong(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Something went wrong."


class DuplicateEmail(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Duplicate email."


class ExpiredOrInvalidCode(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Code might expired or invalid."


class InvalidCredentials(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Invalid credentials."
        self.headers = {"WWW-Authenticate": "Bearer"}


class NotActiveAccount(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Activate account first."


class ForbiddenException(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "Forbidden token."


class WrongRefreshToken(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Refresh token is invalid."
