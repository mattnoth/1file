import os
import re
import sys
import tiktoken
import nltk
from nltk.corpus import stopwords
from datetime import datetime
import xml.etree.ElementTree as ET
import time

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
    if filename.startswith('.'):
        return False
        
    excluded_files = {
        'package-lock.json',
        'package.json',
        'tsconfig.json',
        'next-env.d.ts',
        'next.config.ts',
        'yarn.lock',
        'pnpm-lock.yaml'
    }
    
    if filename in excluded_files:
        return False
        
    allowed_extensions = ['.py', '.txt', '.js', '.tsx', '.ts', '.md', 
                         '.cjs', '.html', '.json', '.ipynb', '.h', 
                         '.localhost', '.sh', '.yaml', '.example', '.cs']
    
    return any(filename.endswith(ext) for ext in allowed_extensions)

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

def process_csharp_file(content):
    def escape_non_xml(text):
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    def balance_brackets(text):
        stack = []
        start = 0
        for i, char in enumerate(text):
            if char == '<':
                stack.append(i)
            elif char == '>' and stack:
                start = stack.pop()
                if not stack:
                    yield (start, i + 1)

    xml_comment_pattern = r'(///.*?$|/\*\*(?:(?!\*/).)*?\*/)'
    
    parts = re.split(xml_comment_pattern, content, flags=re.MULTILINE | re.DOTALL)

    processed_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 0:  # This is a code part
            last_end = 0
            for start, end in balance_brackets(part):
                processed_parts.append(escape_non_xml(part[last_end:start]))
                processed_parts.append(part[start:end])
                last_end = end
            processed_parts.append(escape_non_xml(part[last_end:]))
        else:  # This is an XML comment part
            processed_parts.append(part)

    return ''.join(processed_parts)

def process_file(file_path, local_path):
    relative_path = os.path.relpath(file_path, local_path)
    content = safe_file_read(file_path)
    
    if file_path.endswith('.cs'):
        content = process_csharp_file(content)
    else:
        content = escape_xml(content)
    
    file_content = f'<file name="{escape_xml(relative_path)}">{content}</file>'
    token_count = get_token_count(file_content)
    return file_content, token_count

def process_single_file(file_path):
    if not is_allowed_filetype(os.path.basename(file_path)):
        raise ValueError(f"File type not allowed: {file_path}")
        
    content = [f'<source type="single_file" path="{escape_xml(file_path)}">']
    file_xml, token_count = process_file(file_path, os.path.dirname(file_path))
    content.append(file_xml)
    content.append('</source>')
    
    final_content = '\n'.join(content)
    return final_content, token_count

def process_local_directory(local_path):
    content = [f'<source type="local_directory" path="{escape_xml(local_path)}">']
    total_tokens = 0
    file_count = 0
    start_time = time.time()

    excluded_dirs = {
        'node_modules', 'output', 'obj',
        '.azuredevops', '.git', '.idea', '.vscode', '.next',
        'dist', 'build', 'coverage', 'out',
        'cache', '__pycache__', '.pytest_cache', 'test', 'stacks'
    }

    for root, dirs, files in os.walk(local_path):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        print(f"Entering directory: {root}")
        for file in files:
            if is_allowed_filetype(file):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                try:
                    file_xml, file_tokens = process_file(file_path, local_path)
                    content.append(file_xml)
                    total_tokens += file_tokens
                    file_count += 1

                    if file_count % 10 == 0:
                        elapsed_time = time.time() - start_time
                        files_per_second = file_count / elapsed_time
                        remaining_files = len(files) - file_count
                        estimated_time = remaining_files / files_per_second
                        print(f"Processed {file_count} files. Estimated time remaining: {estimated_time:.2f} seconds")

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    content.append('</source>')
    final_content = '\n'.join(content)
    return final_content, total_tokens

def main():
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = input("Enter the file or directory path: ")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'output')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    date = datetime.now().strftime("%Y%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    path_parts = os.path.normpath(input_path).split(os.sep)
    last_part = path_parts[-1]

    try:
        if os.path.isfile(input_path):
            print(f"\nProcessing file: {input_path}\n")
            output_prefix = "file"
            final_output, uncompressed_token_count = process_single_file(input_path)
        else:
            print(f"\nProcessing directory: {input_path}\n")
            output_prefix = "dir"
            last_part = '-'.join(path_parts[-2:]) if len(path_parts) > 1 else last_part
            final_output, uncompressed_token_count = process_local_directory(input_path)

        output_file = os.path.join(output_dir, f"{date}-uncompressed{output_prefix}_{last_part}_{time_str}.txt")
        processed_file = os.path.join(output_dir, f"{date}-compressed{output_prefix}-{last_part}_{time_str}.txt")

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(final_output)

        compressed_output = preprocess_text(final_output)
        with open(processed_file, "w", encoding="utf-8") as file:
            file.write(compressed_output)

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