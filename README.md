# inno-chat-cleaner

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-2.13-blue.svg)
![Dokku](https://img.shields.io/badge/Dokku-Deployable-blue.svg)
![Docker](https://img.shields.io/badge/Docker-blue.svg)

Simplest bot for removing join/left notifications in Telegram chats. Built with Python and aiogram, this bot can automatically delete messages about users joining or leaving a group. It also requests admin privileges upon being added to a group to perform message deletion.

## Features

- Automatically deletes join/leave messages in groups.
- Requests admin privileges upon being added to a group for message management.
- Error handling for message deletion failures.
- Logging for monitoring and troubleshooting.

## Prerequisites

- Python 3.9 or newer
- Docker and Docker Compose (for Docker deployment)
- A Dokku server (for Dokku deployment)

## Setup and Deployment

### Using Docker Compose

1. Clone this repository:

`git clone https://github.com/IgorDuino/inno-chat-cleaner.git`
`cd inno-chat-cleaner`

2. Create a `.env` file in the root directory with your Telegram bot token:

```env
TELEGRAM_API_TOKEN=your_telegram_bot_token
```

3. Build and run the container:

`docker-compose up --build`

### Deploying with Dokku

1. On your Dokku server, create a new app:

`dokku apps:create inno-chat-cleaner`

2. Set the environment variable for your Telegram bot token:

`dokku config:set inno-chat-cleaner TELEGRAM_API_TOKEN=your_telegram_bot_token`

3. Add the Dokku remote to your local repository:

`git remote add dokku dokku@your-dokku-server.com:inno-chat-cleaner`

4. Push your app to Dokku:

`git push dokku master`

## Usage

Once deployed, the bot will start monitoring for join/leave messages and delete them automatically. It will also request admin privileges upon being added to a group to ensure it has the necessary permissions to manage messages.
