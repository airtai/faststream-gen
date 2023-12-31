# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Embeddings_CLI.ipynb.

# %% auto 0
__all__ = ['app', 'generate']

# %% ../../nbs/Embeddings_CLI.ipynb 1
from typing import *
import shutil
import re
import os
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from pathlib import Path

from langchain.document_loaders import UnstructuredMarkdownLoader, DirectoryLoader, TextLoader
from langchain.schema.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from yaspin import yaspin
import typer


from faststream_gen._code_generator.constants import (
    FASTSTREAM_REPO_ZIP_URL,
    FASTSTREAM_DOCS_DIR_SUFFIX,
    FASTSTREAM_GEN_REPO_ZIP_URL,
    FASTSTREAM_GEN_EXAMPLES_DIR_SUFFIX,
    FASTSTREAM_EXAMPLE_FILES,
    FASTSTREAM_TMP_DIR_PREFIX,
    FASTSTREAM_DIR_TO_EXCLUDE,
    FASTSTREAM_ROOT_DIR_NAME,
    FASTSTREAM_EN_DOCS_DIR,
)
from .package_data import get_root_data_path
from .._code_generator.helper import download_and_extract_github_repo

# %% ../../nbs/Embeddings_CLI.ipynb 3
def _create_documents(
    extrated_path: Path,
    extension: str = "**/*.md",
    dir_to_exclude: str = FASTSTREAM_DIR_TO_EXCLUDE,
) -> List[Document]:
    """Create a List of Document objects from files.

    Args:
        extracted_path (Path): The path to the directory containing the files to be
            loaded as documents.
        extension (str, optional): The file extension pattern to match. Defaults to
            "**/*.md" to match Markdown files in all subdirectories.
        dir_to_exclude (str, optional): Directory to exclude while creating the document object

    Returns:
        List[Document]: A list of documents created from the loaded files.
    """
    api_directory = extrated_path / dir_to_exclude
    if api_directory.exists() and api_directory.is_dir():
        shutil.rmtree(api_directory)

    loader_cls = TextLoader if extension == "*.txt" else UnstructuredMarkdownLoader
    loader = DirectoryLoader(str(extrated_path), glob=extension, loader_cls=loader_cls) # type: ignore
    docs = loader.load()

    typer.echo("\nBelow files are included in the embeddings:")
    typer.echo(
        "\n".join(
            [
                f'    - {d.metadata["source"].replace(f"{extrated_path}/", "")}'
                for d in docs
            ]
        )
    )
    return docs

# %% ../../nbs/Embeddings_CLI.ipynb 5
def _split_document_into_chunks(
    documents: List[Document],
    separator: str,
    chunk_size: int = 500,
    chunk_overlap: int = 0,
) -> List[Document]:
    """Split the list of documents into chunks

    Args:
        documents: List of documents to be split into chunks.
        separators: List of separator patterns used for chunking.
        chunk_size: The maximum size of each chunk in characters. Defaults to 1500.
        chunk_overlap: The overlap between consecutive chunks in characters. Defaults to 150.

    Returns:
        A list of documents where each document represents a chunk.
    """
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separator=separator
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

# %% ../../nbs/Embeddings_CLI.ipynb 7
def _save_embeddings_db(doc_chunks: List[Document], db_path: Path) -> None:
    """Save the embeddings in a FAISS db
    
    Args:
        doc_chunks: A list of documents where each document represents a chunk.
        db_path: Path to save the FAISS db.
    """
    db = FAISS.from_documents(doc_chunks, OpenAIEmbeddings())
    db.save_local(str(db_path))

# %% ../../nbs/Embeddings_CLI.ipynb 9
def _delete_directory(d: str) -> None:
    """Delete a directory and its contents if it exists.

    Args:
        directory_path: The path to the directory to be deleted.
    """
    d_path = Path(d)
    if d_path.exists():
        try:
            shutil.rmtree(d_path)
        except Exception as e:
            print(f"Error deleting directory: {e}")

# %% ../../nbs/Embeddings_CLI.ipynb 11
def _read_lines_from_file(file_path: Path, lines_spec: str) -> str:
    with open(file_path, "r") as file:
        all_lines = file.readlines()

    # Check if lines_spec is empty (indicating all lines should be read)
    if not lines_spec:
        return "".join(all_lines)

    selected_lines = []
    line_specs = lines_spec.split(",")

    for line_spec in line_specs:
        if "-" in line_spec:
            # Handle line ranges (e.g., "1-10")
            start, end = map(int, line_spec.split("-"))
            selected_lines.extend(all_lines[start - 1 : end])
        else:
            # Handle single line numbers
            line_number = int(line_spec)
            if 1 <= line_number <= len(all_lines):
                selected_lines.append(all_lines[line_number - 1])

    return "".join(selected_lines)


def _extract_lines(embedded_line: str, root_path: Path) -> str:
    to_expand_path = re.search("{!>(.*)!}", embedded_line).group(1).strip() # type: ignore 
    lines_spec = ""
    if "[ln:" in to_expand_path:
        to_expand_path, lines_spec = to_expand_path.split("[ln:")
        to_expand_path = to_expand_path.strip()
        lines_spec = lines_spec[:-1]

    if Path(f"{root_path}/docs/docs_src").exists():
        to_expand_path = Path(f"{root_path}/docs") / to_expand_path
    elif Path(f"{root_path}/docs_src").exists():
        to_expand_path = Path(f"{root_path}/") / to_expand_path
    else:
        raise ValueError(f"Couldn't find docs_src directory")
    return _read_lines_from_file(to_expand_path, lines_spec)


def _expand_markdown(
    input_markdown_path: Path,
    output_markdown_path: Path,
    root_path: Path
) -> None:
    with open(input_markdown_path, "r") as input_file, open(
        output_markdown_path, "w"
    ) as output_file:
        for line in input_file:
            # Check if the line does not contain the "{!>" pattern
            if "{!>" not in line:
                # Write the line to the output file
                output_file.write(line)
            else:
                output_file.write(_extract_lines(embedded_line=line, root_path=root_path))

# %% ../../nbs/Embeddings_CLI.ipynb 12
def _expand_faststream_docs(root_path: Path) -> None:
    docs_suffix = root_path / FASTSTREAM_DOCS_DIR_SUFFIX
    docs_suffix.mkdir(exist_ok=True)
    md_files = (root_path / FASTSTREAM_EN_DOCS_DIR).glob("**/*.md")

    def expand_doc(input_path: Path) -> None:
        relative_path = os.path.relpath(input_path, docs_suffix)
        output_path = docs_suffix / relative_path.replace("../docs/docs/en/", "")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _expand_markdown(
            input_markdown_path=input_path, output_markdown_path=output_path, root_path=root_path
        )

    for md_file in md_files:
        expand_doc(md_file)

# %% ../../nbs/Embeddings_CLI.ipynb 14
def _generate_docs_db(input_path: Path, output_path: Path) -> None:
    """Generate Document Embeddings Database.

    This function creates document embeddings for a collection of documents
    located in the specified input directory and saves the embeddings database
    to the specified output directory.

    Args:
        input_path (Path): The path to the directory containing the extracted files.
        output_path (Path): The path to the directory where the embeddings
            database will be saved.
    """
    with yaspin(
        text="Creating embeddings for the docs...", color="cyan", spinner="clock"
    ) as sp:
        _expand_faststream_docs(input_path / FASTSTREAM_ROOT_DIR_NAME)

        docs = _create_documents(input_path / FASTSTREAM_ROOT_DIR_NAME / FASTSTREAM_DOCS_DIR_SUFFIX) 
        _save_embeddings_db(docs, output_path)

        sp.text = ""
        sp.ok(f" ✔ Docs embeddings created and saved to: {output_path}")

# %% ../../nbs/Embeddings_CLI.ipynb 16
def _check_all_files_exist(d: Path, required_files: List[str]) -> bool:
    """Check if all required files exist in a directory.

    Args:
        d (Path): The path to the directory where the existence of files will
            be checked.
        required_files (List[str]): A list of filenames that should exist in
            the directory.

    Returns:
        True if all required files exist in the directory, False otherwise.
    """
    return all((d / file_name).exists() for file_name in required_files)

# %% ../../nbs/Embeddings_CLI.ipynb 19
def _append_file_contents(d: Path, parent_d: Path, required_files: List[str]) -> None:
    """Append contents of specified files to a result file.

    This function appends the contents of the specified list of files to a
    result file in a designated directory.

    Args:
        d (Path): The path to the directory containing the files to be appended.
        parent_d (Path): The parent directory where the result file will be created.
        required_files (List[str]): A list of filenames to be appended.
    """
    appended_examples_dir = parent_d / FASTSTREAM_TMP_DIR_PREFIX
    appended_examples_dir.mkdir(parents=True, exist_ok=True)

    result_file_name = appended_examples_dir / f"{d.name}.txt"

    with result_file_name.open("a") as result_file:
        for file_name in required_files:
            with (d / file_name).open("r") as file:
                result_file.write(
                    f"==== {file_name} starts ====\n{file.read()}\n==== {file_name} ends ====\n"
                )

# %% ../../nbs/Embeddings_CLI.ipynb 21
def _format_examples(input_path: Path, required_files: List[str]) -> None:
    """Format Examples by Appending File Contents.

    This function iterates through directories in the specified input path and checks
    if all the required files exist in each directory. If the required files are present,
    it appends their contents to a result file within the input path. If any of the
    required files are missing, it skips the directory and logs a message.

    Args:
        input_path (Path): The path to the directory containing example directories
            with files to be appended.
        required_files (List[str]): A list of filenames that must exist in each example
            directory.
    """
    for directory in input_path.iterdir():
        if directory.is_dir() and _check_all_files_exist(directory, required_files):
            _append_file_contents(directory, input_path, required_files)
        else:
            typer.echo(f"\nRequired files are missing. Skipping directory: {directory}")


def _generate_examples_db(
    input_path: Path,
    output_path: Path,
    required_files: List[str] = FASTSTREAM_EXAMPLE_FILES,
) -> None:
    """Generate Example Embeddings Database.

    This function creates embeddings for a collection of example documents located in
    the specified input directory and saves the embeddings database to the specified
    output directory. It appends the contents of specified files in each example
    directory, splits the concatenated document into chunks based on specified
    separators, and saves the embeddings for each chunk in the output database.

    Args:
        input_path (Path): The path to the directory containing example documents.
        output_path (Path): The path to the directory where the embeddings database
            will be saved.
        required_files (List[str]): A list of filenames that must exist in each
            example directory. Defaults to FASTSTREAM_EXAMPLE_FILES.
    """
    with yaspin(
        text="Creating embeddings for the examples...", color="cyan", spinner="clock"
    ) as sp:
        
        _format_examples(input_path, required_files)
        docs = _create_documents(
            input_path / FASTSTREAM_TMP_DIR_PREFIX, extension="*.txt"
        )
#         doc_chunks = _split_document_into_chunks(
#             docs, separator="==== description.txt ends ===="
#         )
        _save_embeddings_db(docs, output_path)

        sp.text = ""
        sp.ok(f" ✔ Examples embeddings created and saved to: {output_path}")

# %% ../../nbs/Embeddings_CLI.ipynb 23
app = typer.Typer(
    short_help="Download the zipped FastKafka documentation markdown files, generate embeddings, and save them in a vector database.",
)

# %% ../../nbs/Embeddings_CLI.ipynb 24
@app.command(
    "generate",
    help="Download the docs and examples from FastStream repo, generate embeddings, and save them in a vector database.",
)
def generate(
    db_path: str = typer.Option(
        get_root_data_path(),
        "--db_path",
        "-p",
        help="The path to save the vector database.",
    )
) -> None:
    typer.echo(
        f"Downloading documentation and examples for semantic search."
    )
    try:
        _delete_directory(db_path)

        with download_and_extract_github_repo(
            FASTSTREAM_REPO_ZIP_URL
        ) as extracted_path:
            _generate_docs_db(
                extracted_path, Path(db_path) / "docs"
            )

        with download_and_extract_github_repo(
            FASTSTREAM_GEN_REPO_ZIP_URL
        ) as extracted_path:
            _generate_examples_db(
                extracted_path / FASTSTREAM_GEN_EXAMPLES_DIR_SUFFIX,
                Path(db_path) / "examples",
            )

        typer.echo(
            f"\nSuccessfully generated all the embeddings and saved to: {db_path}"
        )
    except Exception as e:
        fg = typer.colors.RED
        typer.secho(f"Unexpected internal error: {e}", err=True, fg=fg)
        raise typer.Exit(code=1)
