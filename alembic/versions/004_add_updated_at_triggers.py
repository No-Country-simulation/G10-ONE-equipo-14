"""Add PostgreSQL triggers that maintain updated_at timestamps.

Revision ID: 004_add_updated_at_triggers
Revises: 003_create_content_entities
"""

from alembic import op


revision = "004_add_updated_at_triggers"
down_revision = "003_create_content_entities"
branch_labels = None
depends_on = None


TRIGGER_TABLES = ("runs", "opportunities", "assets")


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION set_updated_at()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$
        """
    )

    for table_name in TRIGGER_TABLES:
        op.execute(
            f"""
            CREATE TRIGGER trg_{table_name}_set_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at()
            """
        )


def downgrade() -> None:
    for table_name in reversed(TRIGGER_TABLES):
        op.execute(
            f"DROP TRIGGER IF EXISTS trg_{table_name}_set_updated_at ON {table_name}"
        )

    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")
