"""Run using: python -m scripts.cleanup_expired_sessions (with PYTHONPATH=src)."""
import asyncio
import logging
from core.manager_db_async import SessionLocal, async_engine
from core.session_cleanup import purge_expired_sessions


async def main() -> None:
    try:
        async with SessionLocal.begin() as session:
            count = await purge_expired_sessions(session)
        logging.info("Sesiones expiradas eliminadas: %d", count)
        print(f"Sesiones expiradas eliminadas: {count}")
    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
