import os
import json
import asyncio
import httpx
import argparse
from openai import AsyncOpenAI
from openai_helper import OpenAIHelper
from plugin_manager import PluginManager

class TranslationHelper:
    def __init__(self):
        # # Setup proxy configuration
        # http_client = httpx.AsyncClient(
        #     proxies={
        #         "http://": "http://host:port",
        #         "https://": "http://host:port"
        #     }
        # )
        
        self.client = AsyncOpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
            # http_client=http_client
        )
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

    async def translate_text(self, text: str, target_language: str) -> str:
        try:
            prompt = f"You are a professional translator.Translate the given texts and Prompts to {target_language}.Keep any placeholders, variables, or special characters intact,Cause from now on you only receive the sentence/AI Prompts for translating into {target_language}.Maintain the same tone and meaning.Now Translate This To {target_language}:"
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5  # Lower temperature for more consistent translations
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error translating text: {e}")
            return

    async def translate_json_file(self, input_file: str, target_language: str, target_language_code: str):
        try:
            # Read the original JSON file
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Get the English translations as source
            en_translations = data.get('en', {})
            # Get existing translations for target language if they exist
            existing_translations = data.get(target_language_code, {})
            translated_dict = existing_translations.copy()

            # Translate each entry
            print(f"Starting translation to {target_language}...")
            for key, value in en_translations.items():
                existing_value = existing_translations.get(key, None)
                # Skip if already translated
                if key in existing_translations and existing_value:
                    print(f"Skipping already translated key: {key}:\"{existing_value}\"")
                    continue
                
                try:
                    if isinstance(value, list):
                        # Handle list values
                        translated_list = []
                        for item in value:
                            translated_text = await self.translate_text(item, target_language)
                            translated_list.append(translated_text)
                        translated_dict[key] = translated_list
                    else:
                        # Handle string values
                        translated_text = await self.translate_text(value, target_language)
                        translated_dict[key] = translated_text
                    
                    print(f"Translated: {key}:\"{translated_text}\"")
                    # If the translated_text is None, break the translation
                    if translated_text is None:
                        print("The translation is empty, breaking...")
                        break
                except Exception as e:
                    print(f"Error translating key {key}: {e}")
                    # Break the translation
                    break

                # Write updates to file after each successful translation
                data[target_language_code] = translated_dict
                with open(input_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"Translation completed successfully! Updated {target_language} translations.")

        except Exception as e:
            print(f"Error processing JSON file: {e}")

async def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Translate JSON file to a target language')
    parser.add_argument('target_language', help='Target language name (e.g., "Persian (Farsi)")')
    parser.add_argument('language_code', help='Target language code (e.g., "fa")')
    args = parser.parse_args()

    translator = TranslationHelper()
    await translator.translate_json_file(
        input_file='../translations.json',
        target_language=args.target_language,
        target_language_code=args.language_code
    )

if __name__ == '__main__':
    asyncio.run(main())