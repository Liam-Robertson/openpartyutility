import os
import logging
import time
from openai import OpenAI
import tiktoken

client = OpenAI()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# The max number of tokens in a context window is 128,000 (i.e. you can give it 128,000 tokens)
# However the maximum that you can receive in return is only 4,096 tokens
# For that reason I've set my input tokens at about 8000 tokens so the output will be about half
MAX_RETRIES = 5
INITIAL_BACKOFF = 1
MAX_TOKENS = 8000   # 128,000 max

def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None

def chunk_text_by_tokens(text, max_tokens=MAX_TOKENS, model="gpt-4o"):
    tokenizer = tiktoken.encoding_for_model(model)
    tokens = tokenizer.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(tokenizer.decode(chunk_tokens))

    logger.info(f"Text chunked into {len(chunks)} token-based parts.")
    return chunks

def call_openai_with_retries(prompt, model="gpt-4o"):
    retries = 0
    backoff = INITIAL_BACKOFF

    while retries < MAX_RETRIES:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                retries += 1
                wait_time = backoff * 2 ** retries
                logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Error during GPT completion request: {e}")
                return None
    logger.error("Max retries exceeded.")
    return None

def summarize_text_chunk(text_chunk, file_name):
    prompt = f"""
    Don't cite your sources

    With the following text, do this:
    - A detailed summary of the text that is about half as long as the original
    """
    logger.info(f"Summarizing text chunk for {file_name}")
    return call_openai_with_retries(prompt + text_chunk)

def write_summary_to_file(output_folder, file_name, summary):
    output_path = os.path.join(output_folder, f"Summary - {file_name.replace('.txt', '')}.txt")
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(summary)
        logger.info(f"Summary written to {output_path}")
    except Exception as e:
        logger.error(f"Error writing summary to {output_path}: {e}")

def summarize_texts_in_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Created output folder at {output_folder}")

    for file_name in os.listdir(input_folder):
        input_path = os.path.join(input_folder, file_name)
        if os.path.isfile(input_path) and file_name.endswith('.txt'):
            logger.info(f"Processing {input_path}...")
            text = read_text_file(input_path)
            if not text:
                logger.error(f"Failed to read text for {file_name}")
                continue

            chunks = chunk_text_by_tokens(text)
            summaries = []
            for chunk in chunks:
                summary = summarize_text_chunk(chunk, file_name)
                if summary:
                    summaries.append(summary)
                else:
                    logger.error(f"Failed to generate summary for chunk in {file_name}")
                    break

            if summaries:
                full_summary = "\n\n".join(summaries)
                write_summary_to_file(output_folder, file_name, full_summary)

    logger.info("Summarization of all text files completed.")

if __name__ == "__main__":
    input_folder = 'python/summariseTextTranscription/resources/inputTextTranscriptions'
    output_folder = 'python/summariseTextTranscription/resources/outputTextSummary'
    summarize_texts_in_folder(input_folder, output_folder)
