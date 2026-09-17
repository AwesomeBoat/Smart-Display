import asyncio

async def dire_bonjour():
    print("Bonjour")
    await asyncio.sleep(1)
    print("Fonction dire_bonjour terminée")

async def dire_aurevoir():
    print("aurevoir")
    await asyncio.sleep(1)
    print("fonction dire_aurevoir terminée")

async def main():
    await asyncio.gather(
        dire_bonjour(),
        dire_aurevoir()
    )


def test_yield():
    i = 0
    yield i
    i += 1
    yield i
    i += 1
    yield i


async def final_test(n):
        i = 0
        for loop in range(n):
            yield i
            i += 1 
            await asyncio.sleep(1)

async def final_main(i):
    async for response in final_test(i):
         print(response)

asyncio.run(final_main(3))


# asyncio.run(main())