import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from io import BytesIO
from PIL import Image
from rembg import remove

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
TOKEN = "8129685312:AAHRsV0JW4WpMVYPg3KnS2sLh0RrNRTGuY0"  # Replace with your actual bot token from BotFather

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to Background Remover Bot!\n\n"
        "Just send me any image, and I'll remove the background for you.\n"
        "Type /help for more information."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    await update.message.reply_text(
        "📖 *Background Remover Bot Help*\n\n"
        "This bot uses AI to remove backgrounds from your images.\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "*How to use:*\n"
        "1. Simply send or forward an image to this bot\n"
        "2. Wait a moment while the AI processes your image\n"
        "3. Receive your image with the background removed\n\n"
        "The bot supports JPG, PNG, and other common image formats.",
        parse_mode="Markdown"
    )

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the user's image and remove the background."""
    # Send a processing message
    processing_message = await update.message.reply_text("🔄 Processing your image... Please wait.")
    
    try:
        # Get the photo with the largest size
        photo = update.message.photo[-1]
        
        # Get the file from Telegram servers
        file = await context.bot.get_file(photo.file_id)
        
        # Download the image
        image_url = file.file_path
        response = requests.get(image_url)
        
        if response.status_code == 200:
            # Open the image with Pillow
            input_image = Image.open(BytesIO(response.content))
            
            # Remove the background
            await update.message.reply_text("🧠 AI is removing the background...")
            output_image = remove(input_image)
            
            # Save the processed image to a BytesIO object
            output_buffer = BytesIO()
            output_image.save(output_buffer, format="PNG")
            output_buffer.seek(0)
            
            # Send the processed image back to the user
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=processing_message.message_id
            )
            await update.message.reply_photo(
                output_buffer,
                caption="✨ Here's your image with the background removed!"
            )
        else:
            await update.message.reply_text("❌ Failed to download the image. Please try again.")
            
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        await update.message.reply_text(
            "❌ Sorry, an error occurred while processing your image. Please try again with a different image."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, process_image))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()