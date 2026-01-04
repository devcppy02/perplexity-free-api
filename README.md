allows you to use a public API Perplexity.ai bypassing Cloudflare

```python
import asyncio

from perplexity_free_api_client import PerplexityFreeAPIClient


async def main():
    client = PerplexityFreeAPIClient(cookies=...)
    print(await client.ask(message="Tell me about yourself", model_preference="gpt52"))


if __name__ == "__main__":
    asyncio.run(main())
```
