"""create super-admin role and user

Revision ID: 55897ac14388
Revises: 630f9757e92c
Create Date: 2026-03-25 21:43:47.741993

"""
from typing import Sequence, Union

from alembic import op
import bcrypt
import sqlalchemy as sa

from models import User


# revision identifiers, used by Alembic.
revision: str = '55897ac14388'
down_revision: Union[str, Sequence[str], None] = '630f9757e92c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    res = conn.execute(
        sa.text("INSERT INTO roles (name) VALUES ('superadmin') RETURNING id")
    )
    role_id = res.scalar()

    salt = bcrypt.gensalt()
    password = "admin".encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt = salt)

    stmt = sa.insert(User).values(
        {
            "first_name": "Super",
            "last_name": "Admin",
            "patronymic": "Admin",   
            "email": "admin@admin.com",
            "password": hashed_password.decode(encoding="utf-8"),
            "is_active": True,
            "role_id": role_id
        }
    )

    conn.execute(stmt)


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    conn.execute(
        sa.text("DELETE FROM users WHERE email = 'admin@admin.com'")
    )

    conn.execute(
        sa.text("DELETE FROM roles WHERE name = 'superadmin'")
    )
