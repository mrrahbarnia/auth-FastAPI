from typing import Annotated, Self
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr,
    field_validator,
    model_validator
)


class RegisterOut(BaseModel):
    email: EmailStr


class RegisterIn(RegisterOut):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                'email': 'user@example.com',
                'password': '12345678',
                'confirmPassword': '12345678'
            }
        ]
    })

    password: Annotated[str, Field(min_length=8)]
    confirm_password: Annotated[str, Field(alias="confirmPassword")]

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords are not the same.")
        return self


class VerifyIn(BaseModel):
    verification_code: Annotated[str, Field(alias="verificationCode")]

    @field_validator("verification_code", mode="after")
    @classmethod
    def validate_code_length(cls, value: str) -> str:
        if len(value) != 6:
            raise ValueError("Verification code must be exact 6 chars.")
        return value


class Login(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenIn(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMCwiZXhwIjoxNzMzOTMzODk4fQ.X65KcDJULfXQhjqH2uCPXcjLCO2iNgFVgA3ySmRD-mo"
            }
        ]
    })
    refresh_token: Annotated[str, Field(alias="refreshToken")]
