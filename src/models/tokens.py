from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(nullable=False)