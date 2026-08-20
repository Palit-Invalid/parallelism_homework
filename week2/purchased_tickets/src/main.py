import sys
from pathlib import Path

from granian import Granian
from granian.constants import Interfaces

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.app import create_app
from src.api.exceptions import setup_exception_handlers
from src.config import config
from src.ioc import create_container

container = create_container(config=config)
app = create_app(container=container)
setup_exception_handlers(app=app)


if __name__ == "__main__":
    Granian(target="src.main:app", reload=True, interface=Interfaces.ASGI).serve()
