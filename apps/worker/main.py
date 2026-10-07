import asyncio

from components.interface.worker.app_factory import create_worker_app

app = create_worker_app()

if __name__ == "__main__":
    asyncio.run(app.run())
