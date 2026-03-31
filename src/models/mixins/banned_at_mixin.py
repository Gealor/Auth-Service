from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class BannedAtMixin:
    banned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    