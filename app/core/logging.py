import logging
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.log import Log

class DBHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.engine = create_engine(settings.SQLALCHEMY_DATABASE_URI_SYNC)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def emit(self, record):
        try:
            # Format context
            context = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
                "module": record.module
            }
            if record.exc_info:
                # Basic exception info
                context["exception"] = self.format(record)

            log_entry = Log(
                level=record.levelname,
                logger=record.name,
                message=record.getMessage(),
                module=record.module,
                func_name=record.funcName,
                line_no=record.lineno,
                context=context,
                timestamp=datetime.utcfromtimestamp(record.created),
                duration=getattr(record, "duration", None)
            )

            session = self.SessionLocal()
            try:
                session.add(log_entry)
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        except Exception:
            self.handleError(record)

def setup_logging():
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # Clear existing handlers
    logger.handlers = []

    # Console Handler (WARNING+)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # DB Handler (All logs)
    db_handler = DBHandler()
    db_handler.setLevel(settings.LOG_LEVEL)
    logger.addHandler(db_handler)

    # Set specific log levels for third-party libraries if needed
    logging.getLogger("uvicorn.access").handlers = [] 
