import asyncio
import io
import pygame
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
from asyncio import WindowsSelectorEventLoopPolicy
from RealtimeSTT import AudioToTextRecorder  # Importing RealtimeSTT

# Fix for Windows event loop on Windows
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

token = "TOKEN"
character_id = "ID"
voice_name = "NAME"

# Function to process transcribed text
async def process_text(text, client, chat_session, selected_voice_id, character_id):
    """Process transcribed text and send a response."""
    if text:
        print(f"Transcribed text: {text}")
        response = await client.chat.send_message(character_id, chat_session.chat_id, text)
        print(f"[{response.author_name}]: {response.get_primary_candidate().text}")

        if selected_voice_id:
            generated_speech = await client.utils.generate_speech(
                chat_session.chat_id, response.turn_id, response.get_primary_candidate().candidate_id, selected_voice_id
            )

            audio_stream = io.BytesIO(generated_speech)
            pygame.mixer.init()
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            print("Playing voice response...")

            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
    else:
        print("No valid text received in process_text.")

# Main function to handle the transcription and interaction
async def main():
    recorder = None  # Initialize recorder to ensure it's available in the finally block
    try:
        client = await get_client(token=token)

        # Authenticate and start chat
        user_data = await client.account.fetch_me()
        print(f"Authenticated as @{user_data.username}")
        chat_session, greeting_message = await client.chat.create_chat(character_id)
        print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

        # Select voice
        voice_name = voice_name
        voices = await client.utils.search_voices(voice_name)
        selected_voice = voices[0] if voices else None

        if selected_voice:
            print(f"Selected Voice: {selected_voice.name}")

            # Generate intro speech and play
            selected_voice_id = getattr(selected_voice, 'voice_id', None)
            if not selected_voice_id:
                print("No voice ID found for selected voice.")
                return

            intro_speech = await client.utils.generate_speech(
                chat_session.chat_id, greeting_message.turn_id, greeting_message.get_primary_candidate().candidate_id, selected_voice_id
            )

            audio_stream = io.BytesIO(intro_speech)
            pygame.mixer.init()
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            print("Playing introduction...")

            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

        else:
            print("No voices found.")
            return

        # Initialize RealtimeSTT recorder
        recorder = AudioToTextRecorder()
        recorder.start()  # Start recording

        print("Wait until it says 'speak now'")

        while True:
            # Capture transcribed text
            text = recorder.text()  # This will get the transcribed text from the recorder
            if text:
                print(f"Text received: {text}")
                await process_text(text, client, chat_session, selected_voice_id, character_id)

            await asyncio.sleep(0.1)  # To avoid blocking the loop
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if recorder:
            recorder.stop()  # Stop recording when done
            print("Recording stopped.")

        # Properly close the client session if it was opened
        if hasattr(client, 'session'):
            await client.session.close()
        print("Client session closed.")

# Run the main function asynchronously
if __name__ == '__main__':
    asyncio.run(main())
