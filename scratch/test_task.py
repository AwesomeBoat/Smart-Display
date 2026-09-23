import asyncio

async def randomfunc():
    while True:
        print("hi")
        await asyncio.sleep(1)

async def main():

    asyncio.create_task(randomfunc())
    print("keep going")
    await asyncio.sleep(6)

asyncio.run(main())