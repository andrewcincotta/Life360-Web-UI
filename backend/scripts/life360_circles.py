import asyncio
from aiohttp import ClientSession
from life360 import Life360


async def main():
    # Ask the user for the Life360 authorization token
    authorization: str = "Bearer " + input("Enter your Life360 Bearer token: ")

    # Initialize the Life360 API client with authorization
    async with ClientSession() as session:
        api = Life360(
            session=session,
            authorization=authorization,
            max_retries=3
        )

        circles = await api.get_circles()
        print(circles)

if __name__ == "__main__":
    asyncio.run(main())