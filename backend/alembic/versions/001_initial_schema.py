"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-01-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    user_role_enum = postgresql.ENUM('admin', 'contributor', name='userrole')
    user_role_enum.create(op.get_bind())
    
    development_stage_enum = postgresql.ENUM('concept', 'research', 'prototype', 'testing', 'launch', name='developmentstage')
    development_stage_enum.create(op.get_bind())
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create ideas table
    op.create_table('ideas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('development_stage', development_stage_enum, nullable=False),
        sa.Column('ai_validated', sa.Boolean(), nullable=True),
        sa.Column('ai_refined_pitch', sa.Text(), nullable=True),
        sa.Column('market_potential', sa.DECIMAL(precision=3, scale=1), nullable=True),
        sa.Column('technical_complexity', sa.DECIMAL(precision=3, scale=1), nullable=True),
        sa.Column('resource_requirements', sa.DECIMAL(precision=3, scale=1), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ideas_id'), 'ideas', ['id'], unique=False)
    op.create_index('idx_ideas_created_by', 'ideas', ['created_by'], unique=False)
    op.create_index('idx_ideas_development_stage', 'ideas', ['development_stage'], unique=False)
    op.create_index('idx_ideas_ai_validated', 'ideas', ['ai_validated'], unique=False)
    op.create_index('idx_ideas_created_at', 'ideas', ['created_at'], unique=False)
    
    # Create idea_insights table
    op.create_table('idea_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('idea_id', sa.Integer(), nullable=False),
        sa.Column('market_insights', sa.Text(), nullable=True),
        sa.Column('risk_assessment', sa.Text(), nullable=True),
        sa.Column('implementation_roadmap', sa.Text(), nullable=True),
        sa.Column('is_ai_generated', sa.Boolean(), nullable=True),
        sa.Column('generation_version', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['idea_id'], ['ideas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_idea_insights_id'), 'idea_insights', ['id'], unique=False)
    op.create_index('idx_idea_insights_idea_id', 'idea_insights', ['idea_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index('idx_idea_insights_idea_id', table_name='idea_insights')
    op.drop_index(op.f('ix_idea_insights_id'), table_name='idea_insights')
    op.drop_table('idea_insights')
    
    op.drop_index('idx_ideas_created_at', table_name='ideas')
    op.drop_index('idx_ideas_ai_validated', table_name='ideas')
    op.drop_index('idx_ideas_development_stage', table_name='ideas')
    op.drop_index('idx_ideas_created_by', table_name='ideas')
    op.drop_index(op.f('ix_ideas_id'), table_name='ideas')
    op.drop_table('ideas')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    sa.Enum(name='developmentstage').drop(op.get_bind())
    sa.Enum(name='userrole').drop(op.get_bind())