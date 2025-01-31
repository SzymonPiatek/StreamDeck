from src.application.application import Application
from src.data.settings import settings


def main():
    app = Application(settings=settings)
    app.run()


if __name__ == "__main__":
    main()
