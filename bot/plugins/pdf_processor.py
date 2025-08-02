import io
import subprocess
import os
import logging # Import the logging module
from pathlib import Path
from typing import Dict
from os import getenv, remove
from telegram import Bot

from .plugin import Plugin

# Constants for better readability and maintainability
NOTED_MD_CLI = "bot/src/notedmd-v3.0"
TMP_DIR = Path("/tmp")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NotedMDPlugin(Plugin):
    """
    A plugin to convert handwritten text to markdown using the `noted.md` CLI tool.
    """
    def get_source_name(self) -> str:
        return "NotedMD"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "convert_to_markdown",
            "description": "Convert handwritten notes to Markdown using noted.md.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "The user file ID of the PDF file.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Optional custom prompt to override the default instructions for the LLM."
                    },
                    "pages": {
                        "type": "string",
                        "description": "Optional specific pages or page ranges to convert for PDFs (e.g., '1,3-5,8')."
                    },
                    "pages_per_batch": {
                        "type": "integer",
                        "description": "Optional number of pages to process at once for PDFs (max 30). Default: 1."
                    },
                    "output": {
                        "type": "string",
                        "enum": ["file", "txt"],
                        "description": "Output to user in a file or directly through the messages."
                    }
                },
                "required": ["file_id"], # 'prompt' and 'pages' are optional based on usage
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        logger.info(f"Executing {function_name} with kwargs: {kwargs}")
        file_id = kwargs["file_id"]
        prompt = kwargs.get("prompt")
        pages = kwargs.get("pages")
        pages_per_batch = kwargs.get("pages_per_batch")
        output_format = kwargs.get("output", "txt") # Default to "txt" if not specified
        api_key = getenv('OPENAI_API_KEY')

        local_pdf_path = None
        md_file_path = None

        try:
            # 1. Download the PDF file from Telegram
            logger.info(f"Attempting to download file with ID: {file_id}")
            bot = Bot(getenv('TELEGRAM_BOT_TOKEN'))
            media_file = await bot.get_file(file_id)
            local_pdf_path = TMP_DIR / f"{media_file.file_id}.pdf"
            await media_file.download_to_drive(custom_path=local_pdf_path)
            logger.info(f"File downloaded to: {local_pdf_path}")

            # 2. Configure noted.md provider
            config_command = [NOTED_MD_CLI, "config", "--set-provider", "gemini"]
            logger.info(f"Running NotedMD config command: {' '.join(config_command)}")
            subprocess.run(config_command, check=True, capture_output=True, text=True)
            logger.info("NotedMD provider configured successfully.")

            # 3. Build and execute the conversion command
            convert_command = [NOTED_MD_CLI, "convert", str(local_pdf_path)]

            if prompt:
                convert_command.extend(["--prompt", prompt])
                logger.debug(f"Prompt specified: {prompt}")
            if api_key:
                convert_command.extend(["--api-key", api_key])
                logger.debug("API key added to command.")
            if pages:
                convert_command.extend(["--pages", pages])
                logger.debug(f"Pages specified: {pages}")
            if pages_per_batch:
                convert_command.extend(["--pages-per-batch", str(pages_per_batch)])
                logger.debug(f"Pages per batch specified: {pages_per_batch}")

            md_file_path = local_pdf_path.with_suffix(".md")
            logger.info(f"Running NotedMD convert command: {' '.join(convert_command)}")

            # Execute the conversion
            subprocess.run(convert_command, check=True, capture_output=True, text=True)
            logger.info(f"NotedMD conversion successful. Output expected at: {md_file_path}")

            # 4. Process and return the result based on output_format
            if output_format == "txt":
                logger.info(f"Output format is 'txt'. Reading markdown file: {md_file_path}")
                try:
                    with open(md_file_path, "r") as md_file:
                        md_content = md_file.read()
                    logger.info("Markdown content read successfully.")
                    return {"result": md_content}
                except FileNotFoundError:
                    logger.error(f"Markdown file not found after conversion at {md_file_path}.")
                    return {"error": f"Markdown file not found after conversion at {md_file_path}."}
                except Exception as e:
                    logger.error(f"Error reading markdown file {md_file_path}: {str(e)}")
                    return {"error": f"Error reading markdown file: {str(e)}"}
            else: # output_format == "file"
                logger.info(f"Output format is 'file'. Returning path to markdown file: {md_file_path}")
                return {
                    'direct_result': {
                        'kind': 'file',
                        'format': 'path',
                        'value': str(md_file_path),
                    }
                }

        except subprocess.CalledProcessError as e:
            # Handle errors from subprocess commands
            error_message = f"NotedMD CLI error (return code {e.returncode}): {e.stderr.strip()}"
            logger.error(error_message, exc_info=True)
            return {"error": error_message}
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred during execution: {str(e)}", exc_info=True)
            return {"error": f"An unexpected error occurred: {str(e)}"}
        finally:
            # Clean up temporary files
            if local_pdf_path and local_pdf_path.exists():
                remove(local_pdf_path)
                logger.info(f"Removed temporary PDF file: {local_pdf_path}")
            # Only remove md_file_path if it was generated and output_format was 'txt'
            # If output_format is 'file', the file is expected to be used by the caller.
            if output_format == "txt" and md_file_path and md_file_path.exists():
                remove(md_file_path)
                logger.info(f"Removed temporary Markdown file: {md_file_path}")