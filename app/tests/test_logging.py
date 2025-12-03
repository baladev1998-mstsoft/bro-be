import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.logging import setup_logging
from app.models.log import Log

client = TestClient(app)

# Re-run setup_logging to ensure it picks up the new logic
setup_logging()

# Setup sync DB session for tests
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI_SYNC)
TestingSessionLocal = sessionmaker(bind=engine)

def test_db_logging_configuration():
    # Check if DBHandler is attached
    logger = logging.getLogger()
    db_handler = None
    for handler in logger.handlers:
        if handler.__class__.__name__ == "DBHandler":
            db_handler = handler
            break
    assert db_handler is not None

def test_error_logging_to_db():
    # Trigger a 404 error
    client.get("/api/v1/non-existent-db-logging-test")
    
    # Check if error is logged to DB
    session = TestingSessionLocal()
    try:
        # Query logs
        log_entry = session.query(Log).filter(Log.message.like("%HTTP 404 error%")).order_by(Log.timestamp.desc()).first()
        
        assert log_entry is not None
        assert log_entry.level == "WARNING"
        assert "non-existent-db-logging-test" in log_entry.message
        assert log_entry.context is not None
        assert "file" in log_entry.context
    finally:
        session.close()

def test_request_logging_to_db():
    # Make a successful request
    client.get("/health")
    
    # Check if request is logged to DB
    session = TestingSessionLocal()
    try:
        # Query logs
        log_entry = session.query(Log).filter(Log.message.like("%Request: GET /health%")).order_by(Log.timestamp.desc()).first()
        
        assert log_entry is not None
        assert log_entry.level == "INFO"
        
        # Check response log
        resp_entry = session.query(Log).filter(Log.message.like("%Response: GET /health%")).order_by(Log.timestamp.desc()).first()
        assert resp_entry is not None
        assert "Status: 200" in resp_entry.message
        assert resp_entry.duration is not None
        assert "ms" in resp_entry.duration
    finally:
        session.close()

def test_console_logging_level():
    logger = logging.getLogger()
    
    console_handler = None
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.__class__.__name__ != "DBHandler":
            console_handler = handler
            break
    
    assert console_handler is not None
    assert console_handler.level == logging.WARNING
