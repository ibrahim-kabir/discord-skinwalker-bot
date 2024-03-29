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

1. **Build the Docker image:** Docker Compose will automatically build your
   Docker image if it doesn't exist or if the Dockerfile has changed. You can
   also manually build the Docker image with the docker-compose build command:
   ```cmd
   docker-compose build
   ```
1. **Run the Docker container:** To run your Docker container, you can use the
   docker-compose up command:
   ```
   docker-compose up
   ```

