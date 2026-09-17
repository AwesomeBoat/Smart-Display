import asyncio
import httpx


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



meteo = httpx.get("https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current_weather=true")

data = meteo.json()['current_weather']

curr_temp = data['temperature']
curr_windspeed = data['windspeed']

print(f"Temperature: {curr_temp}\nvitesse du vent: {curr_windspeed}")