-- AI Innovation Incubator Database Schema
-- Production deployment script for PostgreSQL

-- Create database (run this separately if needed)
-- CREATE DATABASE ideaforge_ai;

-- Connect to the database
-- \c ideaforge_ai;

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'contributor');
CREATE TYPE development_stage AS ENUM ('concept', 'research', 'prototype', 'testing', 'launch');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'contributor',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ideas table
CREATE TABLE ideas (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    development_stage development_stage NOT NULL,
    ai_validated BOOLEAN DEFAULT FALSE,
    ai_refined_pitch TEXT,
    market_potential DECIMAL(3,1) DEFAULT 5.0,
    technical_complexity DECIMAL(3,1) DEFAULT 5.0,
    resource_requirements DECIMAL(3,1) DEFAULT 5.0,
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Idea insights table
CREATE TABLE idea_insights (
    id SERIAL PRIMARY KEY,
    idea_id INTEGER NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    market_insights TEXT,
    risk_assessment TEXT,
    implementation_roadmap TEXT,
    is_ai_generated BOOLEAN DEFAULT TRUE,
    generation_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_ideas_created_by ON ideas(created_by);
CREATE INDEX idx_ideas_development_stage ON ideas(development_stage);
CREATE INDEX idx_ideas_ai_validated ON ideas(ai_validated);
CREATE INDEX idx_ideas_created_at ON ideas(created_at);
CREATE INDEX idx_idea_insights_idea_id ON idea_insights(idea_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_ideas_updated_at 
    BEFORE UPDATE ON ideas 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_idea_insights_updated_at 
    BEFORE UPDATE ON idea_insights 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123 - change in production!)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, hashed_password, role) VALUES 
('admin', 'admin@ideaforge.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5W', 'admin');

-- Create sample data (optional - remove for production)
INSERT INTO users (username, email, hashed_password, role) VALUES 
('demo_user', 'demo@ideaforge.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5W', 'contributor');

INSERT INTO ideas (title, description, development_stage, created_by, ai_validated) VALUES 
('AI-Powered Personal Finance Coach', 'An intelligent financial advisor that uses machine learning to provide personalized budgeting and investment advice.', 'concept', 2, false),
('Smart Urban Farming System', 'IoT-enabled vertical farming solution for urban environments with automated nutrient delivery and climate control.', 'research', 2, false);

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;