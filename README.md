# Project Voice-Chat-AI-TTS
### Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation Guide](#installation-guide)
- [Usage](#usage)
- [Additional Documentation](#additional-documentation)
- [License](#license)
- [Issues and Improvements](#issues-and-improvements)
- [Known Bugs](#known-bugs)
- [Contribution](#contribution)

## Overview
Voice-Chat-AI-TTS is a Python-based tool that connects YouTube live chat with a Text-to-Speech (TTS) engine, enabling viewers to interact with a Character.AI model during live streams. Viewers can send messages in the chat, and the AI will generate responses in near real-time. The system uses pytchat to capture live chat messages, PyCharacterAI to generate AI-driven responses, and a TTS engine to convert these responses into speech. This interactive feature enhances audience engagement, making live streams more dynamic and immersive for both streamers and viewers.

## Features
- **YouTube Chat Integration**: Uses pytchat to capture live chat messages from YouTube and converts them into a response to PyCharacterAI.
- **Real-Time Speech to Text**: RealtimeSTT listens the user's voice and submits it as a reponse to PyCharacterAI.
- **Customizable TTS Voices**: Users can choose different voices using Character.AI
- **Message Filtering**: Optional filters can be added as a wake work to the AI.

## Installation Guide
Before you begin, ensure you have the following installed:
- **Python 3.7** or higher.
- Libraries:
  - `pytchat`
  - `pygame`
  - `PyCharacterAI`
  - `RealtimeSTT`

1. Install required libraries using `pip`:
``` bash
pip install pytchat pygame PyCharacterAI RealtimeSTT
```
2. Replace the default YouTube video ID in the script with your live stream video ID:
``` bash
video_id = "ID"
```
- **Note**: Your video ID is found in the URL: youtube.com/live/**WRb7TC2k1cQ**
3. Set your Token by replacing "TOKEN" with your actual API token:
``` bash
token = "TOKEN"
```
- **Note**: Your `TOKEN` can be found using the guide in the PyCharacterAI Github, under [Additional Documentation](#additional-documentation)
4. Set your character ID's by replacing "ID" with the character's unique ID:
``` bash
character_id = "ID"
```
- **Note**: The character ID is found in the URL: character.ai/chat/**vmZa-_m5BORlTH0EA-9tx-a5fiHjPzzGlR63T9DaVQE**
5. Set the speaker's name by replacing "USER" with your desired speaker name:
``` bash
speaker = "USER"
```
- **Example**: Replace `NAME` with MisterZen, or however you want the AI to recognize you by.
6. Set the Voice Name by replacing "NAME" with the character's voice name:
``` bash
voice_name = "NAME"
```
- **Example**: Replace `NAME` with Goku, or whichever voice you want the AI to use.

### **Final Note**: Ensure you have valid credentials for video_id, token, character_id, and voice_name from the appropriate API or configuration.

## Usage
Once set up, the script will begin listening for live YouTube chat messages. When a viewer types a message or when the user's speech mentions a(n) `allowed-word`, the script will process it and have the AI respond to it aloud.

- *Basic Example Usage*:
Viewers type a message like Hello, *Character*! in the chat. The PyCharacterAI reads the message as a reponse, and then the AI will generate a reponse to that message outloud with a chosen voice

## Compatibility
- **Works with YouTube**: The script is tested and optimized for use with YouTube live streams.
- **OS Compatibility**: Compatible with Windows, using Visual Studio Code, not yet tested on macOS or Linux.

## Additional Documentation
Libraries Used:
- pytchat: https://github.com/taizan-hokuto/pytchat
- pygame: https://pypi.org/project/pygame/
- PyCharacterAI: https://github.com/Xtr4F/PyCharacterAI
- RealtimeSTT: https://github.com/KoljaB/RealtimeSTT

## License
This project is licensed under the Creative Commons Attribution 4.0 International License.

**You are free to:**
- Share — copy and redistribute the material in any medium or format.
- Adapt — remix, transform, and build upon the material.

**Under the following terms:**
- Attribution — You must give appropriate credit and indicate if changes were made.

See the LICENSE file for more details.

## Issues and Improvements
If you encounter any issues or have suggestions for improvements, please feel free to submit an issue using the **issues tab** above.

To see a list of planned improvements and future updates, please review the **Roadmap**.

## Known Bugs
- TTS Delay: Depending on network conditions or API limits, there may be occasional delays in the TTS output.

## Contribution
Thank you for visiting this repository! Contributions are optional but always appreciated. You can help by:
- Reporting bugs or issues
- Suggesting features or improvements
- Submitting pull requests
- Starring the repository to show your support

Donations are also welcome to support the project. 

**Support Options:**
- Send a donation via [Cash App](https://cash.app/$MisterZen01)
- Become a YouTube Member starting @ $0.99/mo
- Donate through YouTube Super Chat

### Your involvement means a lot—thank you!
