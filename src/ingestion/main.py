
import argparse
import asyncio

from src.ingestion.config import INGESTION_CONFIGS
from src.ingestion.pipeline import sync_vectorstore


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("key", choices=[*INGESTION_CONFIGS.keys(), "all"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    configs = (
        INGESTION_CONFIGS.values()
        if args.key == "all"
        else [INGESTION_CONFIGS[args.key]]
    )

    for config in configs:
        result = await sync_vectorstore(config, dry_run=args.dry_run)
        print(
            f"{result.collection_name}: "
            f"added={result.added}, "
            f"updated={result.updated}, "
            f"skipped={result.skipped}"
        )


if __name__ == "__main__":
    asyncio.run(main())