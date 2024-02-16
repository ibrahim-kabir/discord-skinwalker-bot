# Voice Detection and Imitation Discord Bot

This Discord bot, called Skinwalker Bot, is designed to add a touch of humor to
voice channels by recording user conversations and randomly repeating amusing or
interesting phrases in the most active channel.

## Functionality Overview

- **Voice Recording**: The bot constantly records audio when users are in voice
  channels.
- **Phrase Repetition**: It joins the most active channel and selects sentences
  said by a random user and repeat it in the active voice channel at random
  intervals.

## Sequence Diagram

![image](https://github.com/ibrahim-kabir/discord-skinwalker-bot/assets/117961703/f4363154-fab4-4930-87f3-2bd6968c241b)

## Usage

1. **Build the Docker Image:** Open a terminal in the directory containing your
   Dockerfile and run the following command to build your Docker image. Replace
   "your-bot-name" with whatever you want to name your Docker image: 
   ```cmd
   docker build -t your-bot-name .
   ```
1. **Run the Docker Container:** Run your bot with the following command: 
    ```cmd
    docker run -d your-bot-name
    ```