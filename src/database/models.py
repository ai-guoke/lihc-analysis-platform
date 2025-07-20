"""
Database models and persistence layer for LIHC Platform
SQLAlchemy-based models for production deployment
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import os
import secrets

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://lihc_user:secure_password_change_in_production@localhost:5432/lihc_platform"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    datasets = relationship("Dataset", back_populates="owner")
    analyses = relationship("Analysis", back_populates="owner")

class Dataset(Base):
    """Dataset model"""
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    data_type = Column(String(50), nullable=False)  # rna_seq, cnv, mutation, methylation
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    samples_count = Column(Integer)
    features_count = Column(Integer)
    quality_score = Column(Float)
    status = Column(String(50), default="uploaded")  # uploaded, processing, ready, error
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="datasets")
    quality_reports = relationship("QualityReport", back_populates="dataset")

class QualityReport(Base):
    """Data quality report model"""
    __tablename__ = "quality_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    overall_score = Column(Float, nullable=False)
    missing_rate = Column(Float)
    outliers_count = Column(Integer)
    duplicates_count = Column(Integer)
    low_variance_features = Column(Integer)
    issues = Column(JSON)  # List of issues detected
    recommendations = Column(JSON)  # List of recommendations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="quality_reports")

class Analysis(Base):
    """Analysis model"""
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    analysis_type = Column(String(50), nullable=False)  # closedloop, integration, etc.
    status = Column(String(50), default="queued")  # queued, running, completed, failed
    progress = Column(Float, default=0.0)
    message = Column(Text)
    parameters = Column(JSON)
    target_genes = Column(JSON)
    results_path = Column(String(500))
    error_message = Column(Text)
    estimated_completion = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Foreign keys
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="analyses")
    dataset_associations = relationship("AnalysisDataset", back_populates="analysis")
    results = relationship("AnalysisResult", back_populates="analysis")

class AnalysisDataset(Base):
    """Many-to-many relationship between analyses and datasets"""
    __tablename__ = "analysis_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    role = Column(String(50))  # primary, secondary, validation, etc.
    
    # Relationships
    analysis = relationship("Analysis", back_populates="dataset_associations")
    dataset = relationship("Dataset")

class AnalysisResult(Base):
    """Analysis results model"""
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_type = Column(String(50), nullable=False)  # causal_genes, networks, pathways
    data = Column(JSON, nullable=False)
    file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="results")

class CausalGene(Base):
    """Causal gene results model"""
    __tablename__ = "causal_genes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gene_id = Column(String(50), nullable=False, index=True)
    gene_symbol = Column(String(50), index=True)
    causal_score = Column(Float, nullable=False)
    confidence_level = Column(String(20))  # High, Medium, Low
    evidence_types = Column(JSON)  # List of evidence types
    differential_expression_score = Column(Float)
    survival_association_score = Column(Float)
    cnv_driver_score = Column(Float)
    methylation_regulation_score = Column(Float)
    mutation_frequency_score = Column(Float)
    biological_context = Column(JSON)
    validation_status = Column(String(50), default="pending")
    literature_support = Column(Boolean, default=False)
    
    # Foreign keys
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    
    # Relationships
    analysis = relationship("Analysis")

class SystemLog(Base):
    """System logging model"""
    __tablename__ = "system_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, etc.
    logger_name = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(100))
    function = Column(String(100))
    line_number = Column(Integer)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"))
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    analysis = relationship("Analysis")

class APIKey(Base):
    """API key management model"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    permissions = Column(JSON)  # List of allowed permissions
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User")

class Session(Base):
    """User session model"""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User")

# Database utilities
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)

def init_db():
    """Initialize database with default data"""
    create_tables()
    
    # Create default admin user
    db = SessionLocal()
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Get admin password from environment or use a secure default warning
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            logger.warning("ADMIN_PASSWORD environment variable not set. Admin user will be created with a random password.")
            admin_password = secrets.token_urlsafe(16)
            logger.warning(f"Generated admin password: {admin_password}")
            logger.warning("Please change this password immediately after first login!")
        
        admin_user = User(
            username="admin",
            email="admin@lihc.ai",
            hashed_password=pwd_context.hash(admin_password),
            full_name="Administrator",
            role="admin"
        )
        
        # Check if admin user exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            db.add(admin_user)
            db.commit()
            print("Created default admin user")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
    print("Database initialized successfully!")