# Furugi Donish Bot

A multilingual Telegram bot for the Furugi Donish educational platform.

## Description

This bot serves as an interface for users to interact with the Furugi Donish educational platform, providing information about services, facilitating contact with administrators, and collecting user feedback.

## Features

- Multi-language support (Tajik, Russian, English)
- Interactive keyboard menu
- User feedback system
- Educational resources information

## Deployment Instructions

### Deploying to Render

1. Sign up for a [Render](https://render.com/) account if you don't have one

2. Create a new Web Service:
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository or use the Render-provided Git repository
   - Enter your repository details

3. Configure the service:
   - Name: `furughi-donish-bot` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn server:app --config gunicorn_config.py`

4. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (already set in code but best to use env var)
   - `WEBHOOK_URL`: Your Render service URL (will look like https://your-service-name.onrender.com)
   - `PORT`: 8080 (or your preferred port)
   - `ENVIRONMENT`: production

5. Deploy the service and wait for the build to complete

6. After successful deployment, your bot should be running and accessible via Telegram

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the bot locally:
   ```
   python furugi_bot.py
   ```

## Notes

- The bot will automatically use webhook mode when deployed to Render
- For local development, it will use polling mode
- Make sure your Telegram bot token is valid
