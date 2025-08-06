import io
import subprocess
import os
import logging  # Import the logging module
from pathlib import Path
from typing import Dict
from os import getenv, remove
from telegram import Bot
import pypandoc  # Import pypandoc for Pandoc conversion

from .plugin import Plugin

# Constants for better readability and maintainability
NOTED_MD_CLI = "./bot/src/notedmd-v3.0"
TMP_DIR = Path("/tmp")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NotedMDPlugin(Plugin):
    """
    A plugin to convert handwritten text to markdown using the `noted.md` CLI tool
    and optionally convert the markdown output to DOCX via pandoc if requested.
    """

    def get_source_name(self) -> str:
        return "NotedMD"

    def get_spec(self) -> [Dict]:
        return [
            {
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
                            "description": "Optional custom prompt to override the default instructions for the LLM.",
                        },
                        "pages": {
                            "type": "string",
                            "description": "Optional specific pages or page ranges to convert for PDFs (e.g., '1,3-5,8').",
                        },
                        "pages_per_batch": {
                            "type": "integer",
                            "description": "Optional number of pages to process at once for PDFs (max 30). Default: 1.",
                        },
                        "output": {
                            "type": "string",
                            "enum": ["file", "txt", "docx"],
                            "description": "Output format: raw markdown text ('txt'), markdown file path ('file'), or docx file path ('docx'). Default is 'txt'.",
                        },
                    },
                    "required": ["file_id"],
                },
            }
        ]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        logger.info(f"Executing {function_name} with kwargs: {kwargs}")
        file_id = kwargs["file_id"]
        prompt = kwargs.get("prompt")
        pages = kwargs.get("pages")
        pages_per_batch = kwargs.get("pages_per_batch")
        output_format = kwargs.get("output", "txt")  # Default to "txt" if not specified
        api_key = getenv("OPENAI_API_KEY")

        local_pdf_path = None
        md_file_path = None

        try:
            # 1. Download the PDF file from Telegram
            logger.info(f"Attempting to download file with ID: {file_id}")
            bot = Bot(getenv("TELEGRAM_BOT_TOKEN"))
            media_file = await bot.get_file(file_id)
            local_pdf_path = TMP_DIR / f"{media_file.file_id}.pdf"
            await media_file.download_to_drive(custom_path=local_pdf_path)
            logger.info(f"File downloaded to: {local_pdf_path}")

            # 2. Configure noted.md provider
            config_command = [NOTED_MD_CLI, "config", "--set-provider", "gemini"]
            logger.info(f"Running NotedMD config command: {' '.join(config_command)}")
            subprocess.run(config_command, check=True, capture_output=True, text=True)
            logger.info("NotedMD provider configured successfully.")

            # 3. Build and execute the noted.md conversion command
            convert_command = [NOTED_MD_CLI, "convert", str(local_pdf_path)]

            if (output_format != 'docx' and prompt):
                convert_command.extend(["--prompt", prompt])
                logger.debug(f"Prompt specified: {prompt}")
            else:
                prompt = """Extract all text from the provided image and convert it into a clean, well-structured Markdown file for reading by students. Ensure of the clean output and ensure that no text is excluded. Pay special attention to the following formatting elements: \

                        - **Headings**: Maintain the hierarchy as presented in the original text.\
                        - **Lists**: Format any lists appropriately.\
                        - **Mathematical Expressions**: Use LaTeX for equations, YOU MUST employ the $$[LATEX-CODE-HERE]$$ syntax instead of the standard code block format.\
                        - **Diagrams and Shapes**:IF YOU KNOW and YOU ARE CERTAIN THAT THE DIAGRAM COULD BE SHOWN USING TikZ, Use TikZ for simple shapes, diagrams, and plots. DO NOT OVER USE IT!
                        - **DO NOT USE PERSIAN SYMBOLS/LETTERS/NUMBERS IN THE TikZ OR LATEX CODE.**
                        - Format TikZ as follows\:

                        tikz
                        \\begin{document}
                        \\begin{tikzpicture}
                        [**TIKZ-CODES-HERE**] 
                        \end{tikzpicture}
                        \end{document}


                        **IMPORTANT INSTRUCTIONS**:\
                        - DO NOT omit any content from the original text or book.\
                        - YOU MUST employ the $$[LATEX-CODE-HERE]$$ syntax instead of the standard code block format for LATEX.
                        - DO NOT USE ANY \`\`\` SIGNS.
                        - DO NOT USE ANY \`\`\` FOR TikZ.
                        - ENCLOSE ANY(I REPEAT, **ANY**) LATEX YOU USE BY $$ SIGN.
                        - **DO NOT USE* $$ IN **MULTIPLE** LINES! OPEN AND CLOSE IN **ONE LINE**!
                        - DO NOT USE [] SIGNS FOR LATEX.
                        - **DO NOT USE PERSIAN SYMBOLS/LETTERS/NUMBERS IN THE TikZ OR LATEX CODE.**
                        - Return the output in a readable and neat format in Persian, omitting any non-understandable parts.\
                        - DO NOT USE unnecessary \begin{document} tags or any other backslash commands, except for TikZ sections.\
                        - Do not reference any unknown image path under any circumstances.\
                        - No explanations on the conversion process are needed; ONLY provide the formatted output."""
                convert_command.extend(["--prompt", prompt])
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

            # 4. Handle output based on selected output_format
            if output_format == "txt":
                # Return markdown content as text
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

            elif output_format == "file":
                # Return markdown file path
                logger.info(f"Output format is 'file'. Returning path to markdown file: {md_file_path}")
                return {
                    "direct_result": {
                        "kind": "file",
                        "format": "path",
                        "value": str(md_file_path),
                    }
                }

            elif output_format == "docx":
                # Convert the markdown file to docx using pypandoc
                output_docx_path = md_file_path.with_suffix(".docx")
                logger.info(
                    f"Converting markdown to docx using pypandoc: {md_file_path} -> {output_docx_path}"
                )
                try:
                    pypandoc.convert_file(
                        str(md_file_path),
                        to="docx",
                        format="latex+raw_tex",
                        outputfile=str(output_docx_path),
                        extra_args=[
                            "-s",
                            "--lua-filter=./bot/src/tikz-filter.lua",
                            "-M",
                            "dir=rtl",
                        ],
                    )
                    logger.info(f"Pandoc conversion successful. Output DOCX at: {output_docx_path}")

                    return {
                        "direct_result": {
                            "kind": "file",
                            "format": "path",
                            "value": str(output_docx_path),
                        }
                    }
                except Exception as e:
                    logger.error(f"Error converting markdown to docx: {str(e)}", exc_info=True)
                    return {"error": f"Failed to convert markdown to docx: {str(e)}"}

            else:
                error_msg = f"Invalid output format specified: {output_format}"
                logger.error(error_msg)
                return {"error": error_msg}

        except subprocess.CalledProcessError as e:
            error_message = f"NotedMD CLI error (return code {e.returncode}): {e.stderr.strip()}"
            logger.error(error_message, exc_info=True)
            return {"error": error_message}

        except Exception as e:
            logger.error(f"An unexpected error occurred during execution: {str(e)}", exc_info=True)
            return {"error": f"An unexpected error occurred: {str(e)}"}

        finally:
            # Clean up files based on output format
            if local_pdf_path and local_pdf_path.exists():
                try:
                    remove(local_pdf_path)
                    logger.info(f"Removed temporary PDF file: {local_pdf_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove PDF file {local_pdf_path}: {e}")

            # Remove markdown file if output is txt (content returned inline)
            if output_format == "txt" and md_file_path and md_file_path.exists():
                try:
                    remove(md_file_path)
                    logger.info(f"Removed temporary Markdown file: {md_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove Markdown file {md_file_path}: {e}")

            # If output is 'file' or 'docx', keep the generated file for user consumption

