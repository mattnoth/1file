1FileLLM is a command-line tool designed to streamline the creation of information-dense prompts for large language models (LLMs). It aggregates and preprocesses data from local directories, compiling them into a single text file.
## Setup
Install the required dependencies:

```bash
pip install -U -r requirements.txt
```

Optionally, create a virtual environment for isolation:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U -r requirements.txt
```

## Usage

***Create a directory- 'output' in the workspace.This is in .gitignore, and anything in this directory will not be processed. It will save previous iterations of the compressed files.***

Run the script using the following command:

```bash
python 1file.py
```

Or pass the path in at the command line:

```bash
python 1file.py /path/to/your/directory
```

### Expected Inputs and Resulting Outputs

The tool supports the following input option:

- Local directory path (e.g., /Users/username/projects/research) -> (files of selected filetypes segmented into one flat text file)

**The output is encapsulated in LLM prompt-appropriate XML.**

The script generates the following output files in the 'output' directory:

- `uncom_[dirname]_[date]-[time].txt`: The full text output.
- `com_[dirname]_[date][time].txt`: Cleaned and compressed text.

## Configuration

- To modify the allowed file types for directory processing, update the `allowed_extensions` list in the code.

## XML Output Format

All output is encapsulated in XML tags. The general structure of the output is as follows:

```xml
<source type="local_directory" path="[directory_path]">
  <file name="[relative_file_path]">
    [File content]
  </file>
  ...
</source>
```

This XML structure provides clear delineation of different files and their contents, potentially improving the LLM's understanding and processing of the input.

## Notes

- Modify this line of code to add or remove filetypes processed:
  ```python
  allowed_extensions = ['.py', '.txt', '.js', '.tsx', '.ts', '.md', '.cjs', '.html', '.json', '.ipynb', '.h', '.localhost', '.sh', '.yaml', '.example']
  ```
- Token counts are displayed in the console for both output files.
- The script automatically skips processing the 'output' directory to avoid including its own output files.
- Progress updates are provided during processing, showing the number of files processed and estimated time remaining.

## Requirements

The script requires the following Python packages:

- tiktoken==0.3.3
- nltk==3.8.1

These requirements are listed in the `requirements.txt` file. 

Run the script using the following command:

```bash
python 1file.py
```

Or pass the path in at the command line:

```bash
python 1file.py /path/to/your/directory
```

### Expected Inputs and Resulting Outputs

The tool supports the following input option:

- Local directory path (e.g., /Users/username/projects/research) -> (files of selected filetypes segmented into one flat text file)

**The output is encapsulated in LLM prompt-appropriate XML.**

The script generates the following output files in the 'output' directory:

- `uncom_[dirname]_[date]-[time].txt`: The full text output.
- `com_[dirname]_[date][time].txt`: Cleaned and compressed text.

## Configuration

- To modify the allowed file types for directory processing, update the `allowed_extensions` list in the code.

## XML Output Format

All output is encapsulated in XML tags. The general structure of the output is as follows:

```xml
<source type="local_directory" path="[directory_path]">
  <file name="[relative_file_path]">
    [File content]
  </file>
  ...
</source>
```

This XML structure provides clear delineation of different files and their contents, potentially improving the LLM's understanding and processing of the input.

## Notes

- Modify this line of code to add or remove filetypes processed:
  ```python
  allowed_extensions = ['.py', '.txt', '.js', '.tsx', '.ts', '.md', '.cjs', '.html', '.json', '.ipynb', '.h', '.localhost', '.sh', '.yaml', '.example']
  ```
- Token counts are displayed in the console for both output files.
- The script automatically skips processing the 'output' directory to avoid including its own output files.
- Progress updates are provided during processing, showing the number of files processed and estimated time remaining.

## Requirements

The script requires the following Python packages:

- tiktoken==0.3.3
- nltk==3.8.1

These requirements are listed in the `requirements.txt` file.
