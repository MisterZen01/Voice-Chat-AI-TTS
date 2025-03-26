import asyncio
import io
import os
import subprocess
import pygame
import pytchat
import threading
from multiprocessing import Queue
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
from asyncio import WindowsSelectorEventLoopPolicy

# Fix for Windows event loop on Windows
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Token and CharacterAI details
token = "TOKEN"
character_id = "ID"
voice_name = "NAME"
video_id = "2novTivLL84"
output_queue = Queue()

def run_realtimestt():
    print("Running RealtimeSTT...")
    try:
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        user_profile = os.environ.get("USERPROFILE", "")
        script_path = os.path.join(user_profile, "path_to__realtimestt_filtered")

        process = subprocess.Popen(
            ['python', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8'
        )

        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                output_queue.put(line)
    except Exception as e:
        print(f"Error running RealtimeSTT: {e}")

async def main():
    client = await get_client(token=token)
    try:
        user_data = await client.account.fetch_me()
        print(f"Authenticated as @{user_data.username}")

        # Create chat session
        chat_session, greeting_message = await client.chat.create_chat(character_id)
        print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

        # Search for Character's voice
        voices = await client.utils.search_voices(voice_name)
        selected_voice = voices[0] if voices else None

        if not selected_voice:
            print("No voices found.")
            return

        selected_voice_id = getattr(selected_voice, 'voice_id', None)
        if not selected_voice_id:
            print("Selected voice has no valid voice_id.")
            return

        print(f"Selected Voice: {selected_voice.name}")

        # Generate and play greeting speech (like in Code 2)
        intro_speech = await client.utils.generate_speech(
            chat_session.chat_id, greeting_message.turn_id, greeting_message.get_primary_candidate().candidate_id, selected_voice_id
        )

        # Play greeting speech using pygame
        audio_stream = io.BytesIO(intro_speech)
        pygame.mixer.init()
        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()
        print("Playing introduction...")

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        # Start RealtimeSTT in a separate thread
        threading.Thread(target=run_realtimestt, daemon=True).start()

        print("Starting Pytchat...")
        chat = pytchat.create(video_id=video_id)  # Replace with actual video ID
        print("Listening to YouTube chat...")

        while True:
            if chat.is_alive():
                for message in chat.get().sync_items():
                    print(f"{message.author.name}: {message.message}")

            while not output_queue.empty():
                stt_text = output_queue.get()
                print(f"RealtimeSTT Detected: {stt_text}")
                response = await client.chat.send_message(character_id, chat_session.chat_id, stt_text)
                print(f"[{response.author_name}]: {response.get_primary_candidate().text}")

                # Generate and play speech for the response using Character's voice
                if selected_voice:
                    try:
                        generated_speech = await client.utils.generate_speech(
                            chat_session.chat_id, response.turn_id, response.get_primary_candidate().candidate_id, selected_voice_id
                        )

                        # Play response speech using pygame
                        audio_stream = io.BytesIO(generated_speech)
                        pygame.mixer.init()
                        pygame.mixer.music.load(audio_stream)
                        pygame.mixer.music.play()
                        print("Playing voice response...")

                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)

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
