# Database Setup Guide

This guide covers setting up the database for the AI Innovation Incubator in both development and production environments.

## Quick Setup Options

### Option 1: Automatic Setup (Recommended)

```bash
# Run the deployment script
python scripts/deploy_database.py
```

### Option 2: Manual SQL Setup

```bash
# For PostgreSQL (production)
psql -U username -d database_name -f sql/init_database.sql
```

### Option 3: Alembic Migrations

```bash
# Run migrations
alembic upgrade head

# Or use the migration script
python scripts/run_migrations.py
```

## Database Schema

### Tables

#### Users Table

- `id` (Primary Key)
- `username` (Unique, 50 chars)
- `email` (Unique, 100 chars)
- `hashed_password` (255 chars)
- `role` (Enum: admin, contributor)
- `created_at` (Timestamp)

#### Ideas Table

- `id` (Primary Key)
- `title` (500 chars)
- `description` (Text)
- `development_stage` (Enum: concept, research, prototype, testing, launch)
- `ai_validated` (Boolean)
- `ai_refined_pitch` (Text, nullable)
- `market_potential` (Decimal 3,1)
- `technical_complexity` (Decimal 3,1)
- `resource_requirements` (Decimal 3,1)
- `created_by` (Foreign Key to users)
- `created_at`, `updated_at` (Timestamps)

#### Idea Insights Table

- `id` (Primary Key)
- `idea_id` (Foreign Key to ideas)
- `market_insights` (Text)
- `risk_assessment` (Text)
- `implementation_roadmap` (Text)
- `is_ai_generated` (Boolean)
- `generation_version` (Integer)
- `created_at`, `updated_at` (Timestamps)

### Indexes

- User username and email (unique)
- Ideas by creator, stage, AI validation status, creation date
- Insights by idea_id

## Environment-Specific Setup

### Development (SQLite)

```bash
# SQLite database is created automatically
export DATABASE_URL="sqlite:///./ai_incubator.db"
python scripts/deploy_database.py
```

### Production (PostgreSQL)

#### Using Supabase

1. Create a Supabase project
2. Get the connection string from Settings → Database
3. Set environment variable:

```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
```

#### Using Render PostgreSQL

1. Database is automatically created via render.yaml
2. Connection string provided as DATABASE_URL environment variable

#### Manual PostgreSQL Setup

```bash
# Create database
createdb ideaforge_ai

# Run setup script
export DATABASE_URL="postgresql://username:password@localhost:5432/ideaforge_ai"
python scripts/deploy_database.py
```

## Migration Management

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description of changes"
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade revision_id

# Downgrade
alembic downgrade -1
```

### Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show head
```

## Default Data

### Admin User

- **Username**: admin
- **Email**: admin@ideaforge.ai
- **Password**: admin123 (⚠️ CHANGE IN PRODUCTION!)
- **Role**: admin

### Sample Data (Development Only)

- Demo user account
- Sample ideas for testing

## Troubleshooting

### Common Issues

**Connection Refused**

- Check database server is running
- Verify connection string format
- Check firewall/network settings

**Permission Denied**

- Verify database user permissions
- Check if user can create tables
- Ensure proper database ownership

**Migration Conflicts**

- Check for conflicting migrations
- Resolve merge conflicts in migration files
- Use `alembic merge` for multiple heads

**Schema Mismatch**

- Compare model definitions with database
- Run `alembic revision --autogenerate` to detect changes
- Check for manual database modifications

### Database URL Formats

**SQLite (Development)**

```
sqlite:///./database.db
```

**PostgreSQL (Production)**

```
postgresql://username:password@host:port/database
```

**Supabase**

```
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

### Health Checks

**Test Database Connection**

```python
from app.database import check_database_connection
print(check_database_connection())
```

**Verify Schema**

```bash
# PostgreSQL
psql -U username -d database -c "\dt"

# SQLite
sqlite3 database.db ".tables"
```

## Security Considerations

### Production Checklist

- [ ] Change default admin password
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS connections
- [ ] Restrict database access by IP
- [ ] Regular database backups
- [ ] Monitor database logs
- [ ] Use connection pooling
- [ ] Implement proper user permissions

### Backup Strategy

```bash
# PostgreSQL backup
pg_dump database_name > backup.sql

# Restore
psql database_name < backup.sql
```

## Performance Optimization

### Recommended Settings

- Connection pooling (5-10 connections)
- Query timeout (30 seconds)
- Connection recycling (5 minutes)
- Enable query logging in development

### Monitoring

- Track slow queries
- Monitor connection usage
- Check index usage
- Regular VACUUM and ANALYZE (PostgreSQL)
