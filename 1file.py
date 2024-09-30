import os
import re
import sys
import tiktoken
import nltk
from nltk.corpus import stopwords
from datetime import datetime
import xml.etree.ElementTree as ET

# Ensure the stopwords are downloaded
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words("english"))

def safe_file_read(filepath, fallback_encoding='latin1'):
    try:
        with open(filepath, "r", encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        with open(filepath, "r", encoding=fallback_encoding) as file:
            return file.read()

def is_allowed_filetype(filename):
    allowed_extensions = ['.py', '.txt', '.js', '.tsx', '.ts', '.md', '.cjs', '.html', '.json', '.ipynb', '.h', '.localhost', '.sh', '.yaml', '.example']
    return any(filename.endswith(ext) for ext in allowed_extensions)

def process_local_directory(local_path):
    content = [f'<source type="local_directory" path="{escape_xml(local_path)}">']
    for root, dirs, files in os.walk(local_path):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        for file in files:
            if is_allowed_filetype(file):
                print(f"Processing {os.path.join(root, file)}...")

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, local_path)
                content.append(f'<file name="{escape_xml(relative_path)}">')

                with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                    content.append(escape_xml(f.read()))

                content.append('</file>')

    content.append('</source>')
    return '\n'.join(content)

def escape_xml(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def get_token_count(text, disallowed_special=[], chunk_size=1000):
    enc = tiktoken.get_encoding("cl100k_base")
    text_without_tags = re.sub(r'<[^>]+>', '', text)
    chunks = [text_without_tags[i:i+chunk_size] for i in range(0, len(text_without_tags), chunk_size)]
    total_tokens = 0
    for chunk in chunks:
        tokens = enc.encode(chunk, disallowed_special=disallowed_special)
        total_tokens += len(tokens)
    return total_tokens

def preprocess_text(input_text):
    def process_text(text):
        text = re.sub(r"[\n\r]+", "\n", text)
        text = re.sub(r"[^a-zA-Z0-9\s_.,!?:;@#$%^&*()+\-=[\]{}|\\<>`~'\"/]+", "", text)
        text = re.sub(r"\s+", " ", text)
        text = text.lower()
        words = text.split()
        words = [word for word in words if word not in stop_words]
        return " ".join(words)

    try:
        root = ET.fromstring(input_text)
        for elem in root.iter():
            if elem.text:
                elem.text = process_text(elem.text)
            if elem.tail:
                elem.tail = process_text(elem.tail)
        return ET.tostring(root, encoding="unicode")
    except ET.ParseError:
        return process_text(input_text)

def main():
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = input("Enter the local directory path: ")

    print(f"\nProcessing directory: {input_path}\n")

    date = datetime.now().strftime("%Y%m%d")
    time = datetime.now().strftime("%H%M%S")
    path_parts = os.path.normpath(input_path).split(os.sep)
    last_two_dirs = '-'.join(path_parts[-2:]) if len(path_parts) > 1 else path_parts[-1]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.getcwd()
    
    if current_dir == script_dir:
        output_dir = os.path.join(script_dir, 'output')
    else:
        output_dir = current_dir

    output_file = os.path.join(output_dir, f"uncom_{last_two_dirs}_{date}-{time}.txt")
    processed_file = os.path.join(output_dir, f"com_{last_two_dirs}_{date}{time}.txt")

    try:
        final_output = process_local_directory(input_path)

        # Write the uncompressed output
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(final_output)

        # Process the compressed output
        compressed_output = preprocess_text(final_output)
        with open(processed_file, "w", encoding="utf-8") as file:
            file.write(compressed_output)

        uncompressed_token_count = get_token_count(final_output)
        compressed_token_count = get_token_count(compressed_output)

        print(f"\nUncompressed Token Count: {uncompressed_token_count}")
        print(f"Compressed Token Count: {compressed_token_count}")
        print(f"\n{output_file} and {processed_file} have been created.")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please check your input and try again.")
        raise
    
if __name__ == "__main__":
    main()