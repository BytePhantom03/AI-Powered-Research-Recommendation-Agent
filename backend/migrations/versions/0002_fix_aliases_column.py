"""Fix aliases column type from ARRAY to JSONB

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-04 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fix the aliases column: drop old ARRAY type and add new JSONB column
    op.execute("ALTER TABLE companies DROP COLUMN IF EXISTS aliases")
    op.add_column('companies', sa.Column('aliases', sa.JSON(), nullable=True))
    
    # Add the progress column to reports if it doesn't exist (was added later)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='reports' AND column_name='progress'
            ) THEN
                ALTER TABLE reports ADD COLUMN progress JSONB;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE companies DROP COLUMN IF EXISTS aliases")
    from sqlalchemy.dialects import postgresql
    op.add_column('companies', sa.Column('aliases', postgresql.ARRAY(sa.String()), nullable=True))
