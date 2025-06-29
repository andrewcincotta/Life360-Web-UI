import asyncio
from aiohttp import ClientSession
from life360 import Life360


async def main():
    # Replace with your actual Life360 Token. Instructions in README.
    authorization = 'Bearer NEJBOUY0Q0EtRTkwNi00N0ZDLTlEOEEtQUFDOTIxMDk0MTc4'

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
