# 1FileLLM: Efficient Data Aggregation for Local Directories

1FileLLM is a command-line tool designed to streamline the creation of information-dense prompts for large language models (LLMs). It aggregates and preprocesses data from local directories, compiling them into a single text file.

## Features

- Support for local directories
- Handling of multiple file formats
- Text preprocessing, including compressed and uncompressed outputs, stopword removal, and lowercase conversion
- Token count reporting for both compressed and uncompressed outputs
- XML encapsulation of output for improved LLM performance

## Installation

### Prerequisites

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

Run the script using the following command:

```bash
python onefilellm.py
```

Or pass the path in at the command line:

```bash
python onefilellm.py /path/to/your/directory
```

### Expected Inputs and Resulting Outputs

The tool supports the following input option:

- Local directory path (e.g., C:\projects\research) -> (files of selected filetypes segmented into one flat text file)

**The output is encapsulated in LLM prompt-appropriate XML.**

The script generates the following output files in the 'output' directory:

- `[timestamp]_uncompressed_[dirname].txt`: The full text output.
- `[timestamp]_compressed_[dirname].txt`: Cleaned and compressed text.

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