import asyncio
import base64
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
video_id="DD1Pmp69wnA"
decoded_token = base64.b64decode("MWE5MjhkYzBkZmVjNzk3YzAyODRhNjQ4YjMxMzA5OThkY2VkY2I5OQ==").decode('utf-8')
character_id = "vmZa-_m5BORlTH0EA-9tx-a5fiHjPzzGlR63T9DaVQE"
speaker = "MisterZen"   #Your name here
voice_name = "Goku"  # Character's voice name
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
    print("Starting RealtimeSTT...")
    try:
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        user_profile = os.environ.get("USERPROFILE", "")
        script_path = os.path.join(user_profile, "Documents", "python_scripts", "Work", "Crowd Control", "pycai_custom_tts", "realtimestt_filtered copy.py")

        process = subprocess.Popen(
            ['python', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8'
        )

        # Continue reading output
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                output_queue.put(line)
            if "speak now" in line:
                print ("Listening to RealtimeSTT...")

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
                if is_allowed_message(message.message):  # Check if the message is allowed
                    print(f"{username}: {message.message}")

                    # Track user interactions and greet users
                    if username not in user_interactions:
                        user_interactions[username] = 1
                        user_prompt = f"How would you greet {username}? {username} then says: {message.message}."
                    else:
                        user_interactions[username] += 1
                        user_prompt = f"{username} said: {message.message}."

                    # Generate and play speech for the response using Character's voice
                    async with chat_lock:  # Ensure only one function accesses chat at a time
                        response = await client.chat.send_message(character_id, chat_session.chat_id, user_prompt)
                        # Check if response is None or invalid
                    print(f"[{response.author_name} to {username}]: {response.get_primary_candidate().text}")

                    try:
                        generated_speech = await client.utils.generate_speech(
                            chat_session.chat_id, response.turn_id, response.get_primary_candidate().candidate_id, selected_voice_id
                        )

                        audio_stream = io.BytesIO(generated_speech)
                        pause_pytchat = True
                        await play_audio(audio_stream)
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

            if is_allowed_message(stt_text):  # Only process allowed STT text
                # Prioritize RealtimeSTT
                print(f"{speaker}: {stt_text}")

                # Track user interactions and greet users
                if speaker not in user_interactions:
                    user_interactions[speaker] = 1
                    user_prompt = f"How would you greet {speaker}?, {speaker} then says: {stt_text}"
                else:
                    user_interactions[speaker] += 1
                    user_prompt = f"{speaker} said: {stt_text}"

                async with chat_lock:  # Ensure only one function accesses chat at a time
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
                    pause_pytchat = True
                    await play_audio(audio_stream)
                    pause_pytchat = False

                except Exception as error:
                    print(f"Speech generation failed: {error}")
                    
        await asyncio.sleep(0.1)

async def main():
    retries = 0
    max_retries = 5
    client = await get_client(token=decoded_token)
    chat_session = await client.chat.create_chat(character_id)
    
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
        await play_audio(audio_stream)

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

        # Retry loop
        while retries < max_retries:
            try:
                if client:
                    print(f"Authenticated as @{user_data.username}")

                if chat_session:
                    print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

                # Voice selection, speech generation, etc. (same as before)

                # Start RealtimeSTT
                threading.Thread(target=run_realtimestt, daemon=True).start()

                print("Starting Pytchat...")
                chat = pytchat.create(video_id=video_id)
                print("Listening to YouTube chat...")

                await asyncio.gather(
                    handle_chat_messages(chat, client, chat_session, selected_voice_id),
                    handle_realtimestt_output(client, chat_session, selected_voice_id)
                )

                break  # If everything works, exit the retry loop.

            except SessionClosedError:
                print("Session closed. Bye!")
                break
            except Exception as error:
                retries += 1
                print(f"An error occurred: {error}")
                print(f"Retrying... Attempt {retries}/{max_retries}")
                await asyncio.sleep(5)
                # Reset client and session to force retry
                client = None
                chat_session = None

    except Exception as error:
        print(f"An error occurred during initial setup: {error}")
    
    # Ensure client session is closed after retries or successful completion.
    if client:
        await client.close_session()
        print("Client session closed.")
    else:
        print("Client was not created.")

async def play_audio(audio_stream):
    global pause_pytchat
    pygame.mixer.init()
    audio_lock = Lock()
    async with audio_lock:
        try:
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            print("Playing voice response...")
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1) # Lower Sleep Time = More Frequent Checks, Higher Sleep Time = Less Frequent Checks
            await asyncio.sleep(1) # Lower Sleep Time = More Frequent Checks, Higher Sleep Time = Less Frequent Checks
        except Exception as e:
            print(f"Error during audio playback: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as error:
        print(f"Runtime Error: {error}")