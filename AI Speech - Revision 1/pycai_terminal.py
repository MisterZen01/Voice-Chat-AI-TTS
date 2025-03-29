import asyncio
import base64
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError

encoded_token = "MWE5MjhkYzBkZmVjNzk3YzAyODRhNjQ4YjMxMzA5OThkY2VkY2I5OQ=="
token = base64.b64decode(encoded_token).decode('utf-8')
character_id = "eUjkmIvLQshQdAb7VuMKqFUz80ZFEp6QfuIxaa3jFGQ"

async def main():
    client = await get_client(token=token)

    me = await client.account.fetch_me()
    print(f"Authenticated as @{me.username}")

    chat, greeting_message = await client.chat.create_chat(character_id)

    print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

    try:
        while True:
            # NOTE: input() is blocking function!
            message = input(f"[{me.name}]: ")

            answer = await client.chat.send_message(character_id, chat.chat_id, message)
            print(f"[{answer.author_name}]: {answer.get_primary_candidate().text}")

    except SessionClosedError:
        print("session closed. Bye!")

    finally:
        # Don't forget to explicitly close the session
        await client.close_session()

asyncio.run(main())
