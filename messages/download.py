import os


async def download_file(session, url: str, filename: str):
    os.makedirs("temp", exist_ok=True)
    filepath = f"temp/{filename}"

    async with session.get(url) as response:
        content = await response.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return filepath
