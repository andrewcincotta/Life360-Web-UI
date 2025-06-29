import asyncio
from aiohttp import ClientSession
from life360 import Life360
import os


async def main():
    # Load the authorization token from environment variable. See .env.example
    authorization = f'Bearer {os.getenv("LIFE360_AUTHORIZATION")}'

    # Initialize the Life360 API client with authorization
    async with ClientSession() as session:
        api = Life360(
            session=session,
            authorization=authorization,
            max_retries=3
        )

        circles = await api.get_circles()

        for circle in circles:
            print("Circle Info: ")
            print(circle)
            members = await api.get_circle_members(circle["id"])
            for member in members:
                print()
                print("Member Info: ")
                print(member)

            print()

if __name__ == "__main__":
    asyncio.run(main())
