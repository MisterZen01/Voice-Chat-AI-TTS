from RealtimeSTT import AudioToTextRecorder

def process_text(text):
        print(f"{text}")  # Print the allowed message

if __name__ == '__main__':
    recorder = AudioToTextRecorder(spinner=False)  # Disable the spinner
    print("speak now")

    while True:
        recorder.text(process_text)
