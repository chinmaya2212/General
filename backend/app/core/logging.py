import logging
import sys
from app.core.config import settings

def setup_logging():
    level = logging.getLevelName(settings.LOG_LEVEL.upper())
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silence excessively noisy loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
