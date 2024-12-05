import sqlalchemy as sa
import sqlalchemy.orm as so

from src.database import Base
from src.auth.type import UserId, UserRole


class User(Base):
    __tablename__ = "users"
    id: so.Mapped[UserId] = so.mapped_column(primary_key=True, autoincrement=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(250), unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(250))
    role: so.Mapped[UserRole] = so.mapped_column(
        sa.Enum(UserRole), default=UserRole.USER
    )
    is_active: so.Mapped[bool] = so.mapped_column(default=False)
