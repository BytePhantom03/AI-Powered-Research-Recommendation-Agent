"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-06-04 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # users table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=True, server_default='free'),
        sa.Column('api_key_hash', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_api_key_hash'), 'users', ['api_key_hash'], unique=False)

    # companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('canonical_slug', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('industry', sa.String(length=255), nullable=True),
        sa.Column('headquarters', sa.String(length=255), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_researched', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True)
    )
    op.create_index(op.f('ix_companies_canonical_slug'), 'companies', ['canonical_slug'], unique=True)

    # reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('company_id', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('company_name_raw', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='PENDING'),
        sa.Column('section_overview', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('section_business_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('section_challenges', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('section_ai_opps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('section_ceo_pitch', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('research_sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('llm_tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('generation_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('pdf_s3_key', sa.String(length=500), nullable=True),
        sa.Column('json_s3_key', sa.String(length=500), nullable=True),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_reports_company_id'), 'reports', ['company_id'], unique=False)
    op.create_index(op.f('ix_reports_status'), 'reports', ['status'], unique=False)
    op.create_index(op.f('ix_reports_user_id'), 'reports', ['user_id'], unique=False)

    # report_events table
    op.create_table(
        'report_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('report_id', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], )
    )
    op.create_index(op.f('ix_report_events_report_id'), 'report_events', ['report_id'], unique=False)

    # usage_logs table
    op.create_table(
        'usage_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('user_id', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )

def downgrade() -> None:
    op.drop_table('usage_logs')
    op.drop_table('report_events')
    op.drop_table('reports')
    op.drop_table('companies')
    op.drop_table('users')
