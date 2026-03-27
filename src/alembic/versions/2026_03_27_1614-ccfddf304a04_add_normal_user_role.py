"""add normal user role

Revision ID: ccfddf304a04
Revises: 5a20c0026484
Create Date: 2026-03-27 16:14:01.864518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccfddf304a04'
down_revision: Union[str, Sequence[str], None] = '5a20c0026484'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    res = conn.execute(
        sa.text("INSERT INTO roles (name) VALUES ('base') RETURNING id")
    )
    role_id = res.scalar()
    
    res = conn.execute(
        sa.text("SELECT id FROM business_elements WHERE name='users'")
    )
    element_id = res.scalar()

    insert_rules_stmt = sa.text("""
        INSERT INTO access_roles_rules (
            role_id, element_id, 
            read_permission, read_all_permission, 
            create_permission, 
            update_permission, update_all_permission, 
            delete_permission, delete_all_permission
        ) VALUES (
            :role_id, :element_id, 
            true, true, false, false, false, false, false
        )
    """)
    conn.execute(
        insert_rules_stmt,[{"role_id": role_id, "element_id": element_id}]
    )

def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    res = conn.execute(
        sa.text("DELETE FROM roles WHERE name='base' RETURNING id")
    )
    role_id = res.scalar()

    delete_rules_by_role_id_stmt = sa.text('''
        DELETE FROM access_roles_rules WHERE role_id = :role_id
    ''')
    conn.execute(delete_rules_by_role_id_stmt, {"role_id": role_id})
