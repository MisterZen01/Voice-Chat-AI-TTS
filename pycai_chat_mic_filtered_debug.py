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
from asyncio import Lock

# Fix for Windows event loop on Windows
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Token and CharacterAI details
token = "TOKEN"
character_id = "ID"
speaker = "USER"   #Your name here
voice_name = "NAME"  # Character's voice name
video_id = "tvBMkY4QDoA"
output_queue = Queue()
user_interactions = {}

# Allowed words or phrases list
allowed_words = [voice_name]  # Add your allowed words here

# Control flag to pause pytchat
pause_pytchat = False

# Lock for controlling concurrent access to chat session
chat_lock = Lock()

class PlaceholderResponse:
    def __init__(self, author_name=voice_name):
        self.author_name = author_name
        self.text = "No response yet."

    def get_primary_candidate(self):
        return self

def run_realtimestt():
    print("Running RealtimeSTT...")
    try:
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        user_profile = os.environ.get("USERPROFILE", "")
        script_path = os.path.join(user_profile, "Documents", "python_scripts", "Work", "Crowd Control", "pycai_custom_tts", "realtimestt_filtered.py")

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

# Function to check if the message contains allowed words
def is_allowed_message(message):
    lower_message = message.lower()
    return any(word.lower() in lower_message for word in allowed_words)

async def handle_chat_messages(chat, client, chat_session, selected_voice_id):
    global pause_pytchat
    response = PlaceholderResponse()

    while True:
        if chat.is_alive() and not pause_pytchat:  # Only process if not paused
            for message in chat.get().sync_items():
                username = message.author.name
                print(f"PYTChat Detected: {username}: {message.message}")
                if is_allowed_message(message.message):  # Check if the message is allowed
                    print(f"PYTChat Allowed: {username}: {message.message}")

                    # Track user interactions and greet users
                    if username not in user_interactions:
                        user_interactions[username] = 1
                        print(f"[{response.author_name}]: Hey {username}, nice to meet you!")
                    else:
                        user_interactions[username] += 1
                        print(f"[{response.author_name}]: Welcome back, {username}!")

                    user_prompt = f"{username} said: {message.message}. How would you like to respond, {response.author_name}?"

                    # Generate and play speech for the response using Character's voice
                    async with chat_lock:  # Ensure only one function accesses chat at a time
                        print(f"Sending message to {response.author_name}: {user_prompt}")
                        response = await client.chat.send_message(character_id, chat_session.chat_id, message.message)
                        # Check if response is None or invalid
                    print(f"[{response.author_name} to {username}]: {response.get_primary_candidate().text}")

                    try:
                        generated_speech = await client.utils.generate_speech(
                            chat_session.chat_id, response.turn_id, response.get_primary_candidate().candidate_id, selected_voice_id
                        )

                        audio_stream = io.BytesIO(generated_speech)
                        pygame.mixer.init()
                        pygame.mixer.music.load(audio_stream)
                        pygame.mixer.music.play()
                        print("Playing voice response...")

                        # Pause pytchat while playing speech
                        pause_pytchat = True

                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)

                        # Resume pytchat after speech finishes
                        pause_pytchat = False

                    except Exception as error:
                        print(f"Speech generation failed: {error}")

        await asyncio.sleep(0.1)

async def handle_realtimestt_output(client, chat_session, selected_voice_id):
    global pause_pytchat
    response = PlaceholderResponse()

    while True:
        if not output_queue.empty() and not pause_pytchat:  # Only process if not paused
            stt_text = output_queue.get()
            print(f"RealtimeSTT Detected: {stt_text}")

            if is_allowed_message(stt_text):  # Only process allowed STT text
                # Prioritize RealtimeSTT
                print(f"RealtimeSTT Allowed: {stt_text}")

                # Track user interactions and greet users
                if speaker not in user_interactions:
                    user_interactions[speaker] = 1
                    print(f"[{response.author_name}]: Hey {speaker}, nice to meet you!")
                else:
                    user_interactions[speaker] += 1
                    print(f"[{response.author_name}]: Welcome back, {speaker}!")

                # Generate personalized message prompt
                user_prompt = f"{speaker} said: {stt_text}. How would you like to respond, {response.author_name}?"

                async with chat_lock:  # Ensure only one function accesses chat at a time
                    print(f"Sending message to {response.author_name}: {user_prompt}")
                    response = await client.chat.send_message(character_id, chat_session.chat_id, user_prompt)
                print(f"[{response.author_name} to {speaker}]: {response.get_primary_candidate().text}")

                # Check if response is None or invalid
                if not response:
                    print(f"Error: No response received from {response.author_name} for message: {stt_text}")
                    continue  # Skip to the next message if no response

                try:
                    generated_speech = await client.utils.generate_speech(
                        chat_session.chat_id, response.turn_id, response.get_primary_candidate().candidate_id, selected_voice_id
                    )

                    audio_stream = io.BytesIO(generated_speech)
                    pygame.mixer.init()
                    pygame.mixer.music.load(audio_stream)
                    pygame.mixer.music.play()
                    print("Playing voice response...")

                    # Pause pytchat while playing speech
                    pause_pytchat = True

                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)

                    # Resume pytchat after speech finishes
                    pause_pytchat = False

                except Exception as error:
                    print(f"Speech generation failed: {error}")
                    
        await asyncio.sleep(0.1)

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

        # Handle both chat messages and RealtimeSTT output concurrently
        await asyncio.gather(
            handle_chat_messages(chat, client, chat_session, selected_voice_id),
            handle_realtimestt_output(client, chat_session, selected_voice_id)
        )

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