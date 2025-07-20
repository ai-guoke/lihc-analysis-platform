"""Initial database schema for LIHC Platform

Revision ID: 001_initial
Revises: 
Create Date: 2024-07-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),  # Match model field name
        sa.Column('full_name', sa.String(length=100), nullable=True),  # Add missing field
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create datasets table
    op.create_table('datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('samples_count', sa.Integer(), nullable=True),
        sa.Column('features_count', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),  # Changed from user_id to match model
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),  # Changed to match column name
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_datasets_data_type'), 'datasets', ['data_type'])
    op.create_index(op.f('ix_datasets_status'), 'datasets', ['status'])
    op.create_index(op.f('ix_datasets_owner_id'), 'datasets', ['owner_id'])  # Changed from user_id

    # Create analyses table
    op.create_table('analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('target_genes', sa.JSON(), nullable=True),
        sa.Column('results_path', sa.String(length=500), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('estimated_completion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_analysis_type'), 'analyses', ['analysis_type'])
    op.create_index(op.f('ix_analyses_status'), 'analyses', ['status'])
    op.create_index(op.f('ix_analyses_owner_id'), 'analyses', ['owner_id'])

    # Create analysis_datasets association table
    op.create_table('analysis_datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create causal_genes table
    op.create_table('causal_genes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('gene_id', sa.String(length=50), nullable=False, index=True),
        sa.Column('gene_symbol', sa.String(length=50), nullable=True, index=True),
        sa.Column('causal_score', sa.Float(), nullable=False),
        sa.Column('confidence_level', sa.String(length=20), nullable=True),
        sa.Column('evidence_types', sa.JSON(), nullable=True),
        sa.Column('differential_expression_score', sa.Float(), nullable=True),
        sa.Column('survival_association_score', sa.Float(), nullable=True),
        sa.Column('cnv_driver_score', sa.Float(), nullable=True),
        sa.Column('methylation_regulation_score', sa.Float(), nullable=True),
        sa.Column('mutation_frequency_score', sa.Float(), nullable=True),
        sa.Column('biological_context', sa.JSON(), nullable=True),
        sa.Column('validation_status', sa.String(length=50), nullable=True),
        sa.Column('literature_support', sa.Boolean(), nullable=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_causal_genes_analysis_id'), 'causal_genes', ['analysis_id'])
    op.create_index(op.f('ix_causal_genes_gene_id'), 'causal_genes', ['gene_id'])

    # Create quality_reports table
    op.create_table('quality_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('missing_rate', sa.Float(), nullable=True),
        sa.Column('outliers_count', sa.Integer(), nullable=True),
        sa.Column('duplicates_count', sa.Integer(), nullable=True),
        sa.Column('low_variance_features', sa.Integer(), nullable=True),
        sa.Column('issues', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create analysis_results table
    op.create_table('analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('result_type', sa.String(length=50), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)

    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False, unique=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_session_token'), 'sessions', ['session_token'], unique=True)

    # Create system_logs table
    op.create_table('system_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('logger_name', sa.String(length=100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('module', sa.String(length=100), nullable=True),
        sa.Column('function', sa.String(length=100), nullable=True),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('additional_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_logs_logger_name'), 'system_logs', ['logger_name'])
    op.create_index(op.f('ix_system_logs_created_at'), 'system_logs', ['created_at'])
    op.create_index(op.f('ix_system_logs_level'), 'system_logs', ['level'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_index(op.f('ix_system_logs_level'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_created_at'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_logger_name'), table_name='system_logs')
    op.drop_table('system_logs')
    
    op.drop_index(op.f('ix_sessions_session_token'), table_name='sessions')
    op.drop_table('sessions')
    
    op.drop_index(op.f('ix_api_keys_key_hash'), table_name='api_keys')
    op.drop_table('api_keys')
    
    op.drop_table('analysis_results')
    
    op.drop_table('quality_reports')
    
    op.drop_index(op.f('ix_causal_genes_gene_id'), table_name='causal_genes')
    op.drop_index(op.f('ix_causal_genes_analysis_id'), table_name='causal_genes')
    op.drop_table('causal_genes')
    
    op.drop_table('analysis_datasets')
    
    op.drop_index(op.f('ix_analyses_owner_id'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_status'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_analysis_type'), table_name='analyses')
    op.drop_table('analyses')
    
    op.drop_index(op.f('ix_datasets_owner_id'), table_name='datasets')
    op.drop_index(op.f('ix_datasets_status'), table_name='datasets')
    op.drop_index(op.f('ix_datasets_data_type'), table_name='datasets')
    op.drop_table('datasets')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')