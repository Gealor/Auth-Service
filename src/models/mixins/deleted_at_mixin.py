from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column


class DeletedAtMixin:
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)