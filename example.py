import asyncio

from perplexity_free_api_client import PerplexityFreeAPIClient


async def main():
    client = PerplexityFreeAPIClient()
    await client.init()

    print(await client.ask(message="Tell me about yourself"))


if __name__ == "__main__":
    asyncio.run(main())
