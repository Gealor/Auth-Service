from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column


class BannedAtMixin:
    banned_at: Mapped[datetime] = mapped_column(nullable=True)
    