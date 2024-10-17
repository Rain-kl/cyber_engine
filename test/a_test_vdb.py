import time

from engine_core.vdb_api import Mnemonic


async def main():
    start=time.time()
    mn = Mnemonic()
    await mn.add("hello", user_id=10001)
    print(f"Time taken: {time.time()-start}")


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
