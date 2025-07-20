-- LIHC Platform Database Initialization Script
-- Creates database schema and initial data for production deployment

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE lihc_platform' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lihc_platform')\\gexec

-- Switch to lihc_platform database
\\c lihc_platform;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create readonly user for Grafana
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'grafana_readonly') THEN
        CREATE USER grafana_readonly WITH PASSWORD 'grafana_readonly_password_change_in_production';
    END IF;
END
$$;

-- Grant readonly permissions
GRANT CONNECT ON DATABASE lihc_platform TO grafana_readonly;
GRANT USAGE ON SCHEMA public TO grafana_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafana_readonly;

-- Create admin user with secure password (change in production)
DO $$
DECLARE
    admin_password text;
BEGIN
    -- Get admin password from environment variable or generate a secure one
    admin_password := coalesce(
        current_setting('app.admin_password', true),
        encode(gen_random_bytes(16), 'base64')
    );
    
    -- Log the generated password for first-time setup
    IF current_setting('app.admin_password', true) IS NULL THEN
        RAISE NOTICE 'Generated admin password: %', admin_password;
        RAISE NOTICE 'IMPORTANT: Save this password and change it after first login!';
    END IF;
    
    INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at, updated_at)
    VALUES (
        uuid_generate_v4(),
        'admin',
        'admin@lihc.platform',
        crypt(admin_password, gen_salt('bf')),
        'admin',
        true,
        now(),
        now()
    ) ON CONFLICT (username) DO NOTHING;
END $$;

-- Create demo user with secure password (development only)
DO $$
DECLARE
    demo_password text;
BEGIN
    -- Only create demo user in development environment
    IF current_setting('app.environment', true) = 'development' THEN
        demo_password := coalesce(
            current_setting('app.demo_password', true),
            'demo_password_' || encode(gen_random_bytes(8), 'base64')
        );
        
        INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at, updated_at)
        VALUES (
            uuid_generate_v4(),
            'demo',
            'demo@lihc.platform',
            crypt(demo_password, gen_salt('bf')),
            'user',
            true,
            now(),
            now()
        ) ON CONFLICT (username) DO NOTHING;
        
        RAISE NOTICE 'Demo user created with password: %', demo_password;
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_datasets_owner_id ON datasets(owner_id);
CREATE INDEX IF NOT EXISTS idx_datasets_data_type ON datasets(data_type);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON datasets(status);
CREATE INDEX IF NOT EXISTS idx_datasets_created_at ON datasets(created_at);

CREATE INDEX IF NOT EXISTS idx_analyses_owner_id ON analyses(owner_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_analysis_type ON analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at);

CREATE INDEX IF NOT EXISTS idx_causal_genes_analysis_id ON causal_genes(analysis_id);
CREATE INDEX IF NOT EXISTS idx_causal_genes_gene_id ON causal_genes(gene_id);
CREATE INDEX IF NOT EXISTS idx_causal_genes_causal_score ON causal_genes(causal_score);

CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);

-- Create function for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON analyses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for automatic cleanup of old logs
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS void AS $$
BEGIN
    -- Delete logs older than 90 days
    DELETE FROM system_logs 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    -- Delete expired sessions
    DELETE FROM sessions 
    WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE 'plpgsql';

-- Create function for analysis statistics
CREATE OR REPLACE FUNCTION get_analysis_stats(user_uuid UUID DEFAULT NULL)
RETURNS TABLE(
    total_analyses INTEGER,
    completed_analyses INTEGER,
    running_analyses INTEGER,
    failed_analyses INTEGER,
    avg_processing_time INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_analyses,
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::INTEGER as completed_analyses,
        COUNT(CASE WHEN status = 'running' THEN 1 END)::INTEGER as running_analyses,
        COUNT(CASE WHEN status = 'failed' THEN 1 END)::INTEGER as failed_analyses,
        AVG(completed_at - started_at) as avg_processing_time
    FROM analyses 
    WHERE (user_uuid IS NULL OR owner_id = user_uuid);
END;
$$ LANGUAGE 'plpgsql';

-- Create function for dataset statistics
CREATE OR REPLACE FUNCTION get_dataset_stats(user_uuid UUID DEFAULT NULL)
RETURNS TABLE(
    total_datasets INTEGER,
    total_samples BIGINT,
    total_features BIGINT,
    avg_quality_score NUMERIC,
    datasets_by_type JSON
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_datasets,
        SUM(samples_count)::BIGINT as total_samples,
        SUM(features_count)::BIGINT as total_features,
        AVG(quality_score)::NUMERIC as avg_quality_score,
        json_object_agg(data_type, type_count) as datasets_by_type
    FROM (
        SELECT 
            data_type,
            COUNT(*) as type_count,
            samples_count,
            features_count,
            quality_score
        FROM datasets 
        WHERE (user_uuid IS NULL OR owner_id = user_uuid)
        GROUP BY data_type, samples_count, features_count, quality_score
    ) subq;
END;
$$ LANGUAGE 'plpgsql';

-- Create materialized view for analysis performance metrics
CREATE MATERIALIZED VIEW analysis_performance_metrics AS
SELECT 
    analysis_type,
    COUNT(*) as total_count,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds,
    MIN(created_at) as first_analysis,
    MAX(created_at) as last_analysis
FROM analyses 
WHERE started_at IS NOT NULL
GROUP BY analysis_type;

-- Create index on materialized view
CREATE UNIQUE INDEX ON analysis_performance_metrics(analysis_type);

-- Create function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_performance_metrics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW analysis_performance_metrics;
END;
$$ LANGUAGE 'plpgsql';

-- Create sample data for testing (commented out for production)
/*
-- Insert sample admin user
INSERT INTO users (id, username, email, hashed_password, full_name, role, is_active)
VALUES (
    uuid_generate_v4(),
    'admin',
    'admin@lihc.ai',
    '$2b$12$example_hash_here',
    'System Administrator',
    'admin',
    true
) ON CONFLICT (username) DO NOTHING;

-- Insert sample regular user
INSERT INTO users (id, username, email, hashed_password, full_name, role, is_active)
VALUES (
    uuid_generate_v4(),
    'researcher',
    'researcher@lihc.ai',
    '$2b$12$example_hash_here',
    'Research User',
    'user',
    true
) ON CONFLICT (username) DO NOTHING;
*/

-- Create backup function
CREATE OR REPLACE FUNCTION create_backup_tables()
RETURNS void AS $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'lihc' AND tablename NOT LIKE 'backup_%'
    LOOP
        EXECUTE format('CREATE TABLE IF NOT EXISTS backup_%s AS SELECT * FROM %s WHERE false', table_name, table_name);
        EXECUTE format('INSERT INTO backup_%s SELECT * FROM %s', table_name, table_name);
    END LOOP;
END;
$$ LANGUAGE 'plpgsql';

-- Grant permissions
GRANT USAGE ON SCHEMA lihc TO lihc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA lihc TO lihc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA lihc TO lihc_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA lihc TO lihc_user;

-- Set up automatic maintenance
-- Schedule cleanup to run daily (this would typically be done with pg_cron extension)
-- SELECT cron.schedule('cleanup-logs', '0 2 * * *', 'SELECT cleanup_old_logs();');
-- SELECT cron.schedule('refresh-metrics', '*/15 * * * *', 'SELECT refresh_performance_metrics();');

-- Final setup message
DO $$
BEGIN
    RAISE NOTICE 'LIHC Platform database initialization completed successfully!';
    RAISE NOTICE 'Schema: lihc';
    RAISE NOTICE 'Tables created with indexes and triggers';
    RAISE NOTICE 'Performance monitoring functions available';
END $$;