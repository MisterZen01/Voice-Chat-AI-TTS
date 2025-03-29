import asyncio
import io
import pygame
import pytchat
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
from asyncio import WindowsSelectorEventLoopPolicy

# Fix for Windows event loop on Windows
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

decoded_token = "TOKEN"
character_id = "ID"
voice_name = "NAME"
video_id = "ID"

async def main():
    client = await get_client(token=decoded_token)

    try:
        user_data = await client.account.fetch_me()
        print(f"Authenticated as @{user_data.username}")

        chat_session, greeting_message = await client.chat.create_chat(character_id)
        print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

        # Search for a specific voice
        voice_name = voice_name  # Replace with actual voice name if known
        voices = await client.utils.search_voices(voice_name)
        selected_voice = voices[0] if voices else None

        if selected_voice:
            print(f"Selected Voice: {selected_voice.name}")

            # Generate and play the introduction voice
            try:
                selected_voice_id = getattr(selected_voice, 'voice_id', None)
                if selected_voice_id is None:
                    raise AttributeError("Selected voice does not have a 'voice_id' attribute.")

                intro_speech = await client.utils.generate_speech(
                    chat_session.chat_id, greeting_message.turn_id, greeting_message.get_primary_candidate().candidate_id, selected_voice_id
                )

                # Play intro using pygame and BytesIO
                audio_stream = io.BytesIO(intro_speech)
                pygame.mixer.init()
                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()
                print("Playing introduction...")

                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)

            except Exception as error:
                print(f"Failed to play introduction: {error}")
        else:
            print("No voices found.")
            return

        # Live chat handler using pytchat
        chat = pytchat.create(video_id=video_id)  # Use the live stream video ID
        print("Listening to YouTube chat...")
        while chat.is_alive():
            for message in chat.get().sync_items():
                user_input = message.message
                author_name = message.author.name

                # Only respond if the voice_name is in the message
                if voice_name.lower() in user_input.lower():
                    print(f"{author_name} says {user_input}")

                    # Send user input to character and get a response
                    response_message = f"{author_name} said: {user_input}"
                    response = await client.chat.send_message(character_id, chat_session.chat_id, response_message)
                    print(f"[{response.author_name}]: {response.get_primary_candidate().text}")

                    # Generate and play speech using the selected voice
                    if selected_voice:
                        try:
                            generated_speech = await client.utils.generate_speech(
                                chat_session.chat_id, response.turn_id, response.get_primary_candidate().candidate_id, selected_voice_id
                            )

                            # Play audio using pygame and BytesIO
                            audio_stream = io.BytesIO(generated_speech)
                            pygame.mixer.init()
                            pygame.mixer.music.load(audio_stream)
                            pygame.mixer.music.play()
                            print("Playing voice response...")

                            while pygame.mixer.music.get_busy():
                                await asyncio.sleep(0.1)

                            # Print "Listening to YouTube chat..." after the voice response is played
                            print("Listening to YouTube chat...")

                        except Exception as error:
                            print(f"Speech generation failed: {error}")

    except SessionClosedError:
        print("Session closed. Bye!")
    except Exception as error:
        print(f"An error occurred: {error}")
    finally:
        await client.close_session()
        print("Client session closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as error:
        print(f"Runtime Error: {error}")
