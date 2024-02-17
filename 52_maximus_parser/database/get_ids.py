import sys
import logging

logger = logging.getLogger(__name__)


async def get_provider_id(db_pool, provider_name):
    try:
        logger.info(f"Started Getting provider id from provider_name: {provider_name}")
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id FROM provider WHERE name = %s", (provider_name,))
                provider_id = await cursor.fetchone()
                logger.info(f"Finished - Retrieved provider id: {provider_id}")
                return provider_id

    except Exception as e:
        logger.error(f"Error while getting provider id: {e}")
        sys.exit(1)


async def get_model_id(db_pool, model_name):
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Check if the model exists in the database
                await cursor.execute("SELECT id FROM model WHERE name = %s", (model_name,))
                model_id = await cursor.fetchone()
                return model_id

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
