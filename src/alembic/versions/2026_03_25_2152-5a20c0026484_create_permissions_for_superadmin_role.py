"""create permissions for superadmin role

Revision ID: 5a20c0026484
Revises: 55897ac14388
Create Date: 2026-03-25 21:52:24.889505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a20c0026484'
down_revision: Union[str, Sequence[str], None] = '55897ac14388'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    # Бизнес элементы, для которых будут строится разрешения
    res = conn.execute(
        sa.text("""
            INSERT INTO business_elements (name) 
            VALUES ('users'), ('roles'), ('permissions')
            RETURNING id
        """)
    )
    element_ids = res.scalars().all()

    # Добавление разрешений
    role_id = conn.execute(
        sa.text("SELECT id FROM roles WHERE name = 'superadmin'")
    ).scalar()
    
    insert_rules_stmt = sa.text("""
        INSERT INTO access_roles_rules (
            role_id, element_id, 
            read_permission, read_all_permission, 
            create_permission, 
            update_permission, update_all_permission, 
            delete_permission, delete_all_permission
        ) VALUES (
            :role_id, :element_id, 
            true, true, true, true, true, true, true
        )
    """)
    conn.execute(
        insert_rules_stmt,[{"role_id": role_id, "element_id": el_id} for el_id in element_ids]
    )
    

def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    conn.execute(
        sa.text("DELETE FROM business_elements WHERE name IN ('users', 'roles', 'permissions')")
    )

