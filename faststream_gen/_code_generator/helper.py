# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Helper.ipynb.

# %% auto 0
__all__ = ['logger', 'examples_delimiter', 'download_and_extract_faststream_archive', 'write_file_contents', 'read_file_contents',
           'validate_python_code', 'set_logger_level', 'get_relevant_prompt_examples', 'CustomAIChat',
           'ValidateAndFixResponse', 'add_tokens_usage']

# %% ../../nbs/Helper.ipynb 1
from typing import *
import random
import time
from contextlib import contextmanager
import functools
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import os
import sys
from collections import defaultdict
import requests
import zipfile

import openai
import typer
from fastcore.foundation import patch
from langchain.schema.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from .._components.logger import get_logger, set_level
from .prompts import SYSTEM_PROMPT
from faststream_gen._code_generator.constants import (
    DEFAULT_PARAMS,
    MAX_RETRIES,
    ASYNC_API_SPEC_FILE_NAME,
    APPLICATION_FILE_NAME,
    TOKEN_TYPES,
    MAX_NUM_FIXES_MSG,
    INCOMPLETE_DESCRIPTION,
    DESCRIPTION_EXAMPLE,
)
from .._components.package_data import get_root_data_path

# %% ../../nbs/Helper.ipynb 3
logger = get_logger(__name__, level=logging.WARNING)

# %% ../../nbs/Helper.ipynb 5
def _fetch_content(url: str) -> requests.models.Response: # type: ignore
    """Fetch content from a URL using an HTTP GET request.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        Response: The response object containing the content and HTTP status.

    Raises:
        requests.exceptions.Timeout: If the request times out.
        requests.exceptions.RequestException: If an error occurs during the request.
    """
    attempt = 0
    while attempt < 4:
        try:
            response = requests.get(url, timeout=50)
            response.raise_for_status()  # Raises an exception for HTTP errors
            return response
        except requests.exceptions.Timeout:
            if attempt == 3:  # If this was the fourth attempt, raise the Timeout exception
                raise requests.exceptions.Timeout(
                    "Request timed out. Please check your internet connection or try again later."
                )
            time.sleep(1)  # Sleep for one second before retrying
            attempt += 1
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"An error occurred: {e}")

# %% ../../nbs/Helper.ipynb 7
@contextmanager
def download_and_extract_faststream_archive(url: str) -> Generator[Path, None, None]:
    with TemporaryDirectory() as d:
        try:
            input_path = Path(f"{d}/archive.zip")
            extrated_path = Path(f"{d}/extrated_path")
            extrated_path.mkdir(parents=True, exist_ok=True)

            response = _fetch_content(url)

            with open(input_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(input_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    zip_ref.extract(member, extrated_path)

            yield extrated_path

        except Exception as e:
            fg = typer.colors.RED
            typer.secho(f"Unexpected internal error: {e}", err=True, fg=fg)
            raise typer.Exit(code=1)

# %% ../../nbs/Helper.ipynb 9
def write_file_contents(output_file: str, contents: str) -> None:
    """Write the given contents to the specified output file.

    Args:
        output_file: The path to the output file where the contents will be written.
        contents: The contents to be written to the output file.

    Raises:
        OSError: If there is an issue while attempting to save the file.
    """
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(contents)

    except OSError as e:
        raise OSError(
            f"Error: Failed to save file at '{output_file}' due to: '{e}'. Please ensure that the specified 'output_path' is valid and that you have the necessary permissions to write files to it."
        )

# %% ../../nbs/Helper.ipynb 11
def read_file_contents(output_file: str) -> str:
    """Read and return the contents from the specified file.

    Args:
        output_file: The path to the file to be read.

    Returns:
        The contents of the file as string.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Error: The file '{output_file}' does not exist. Please ensure that the specified 'output_path' is valid and that you have the necessary permissions to access it."
        )

# %% ../../nbs/Helper.ipynb 14
def validate_python_code(code: str) -> List[str]:
    """Validate and report errors in the provided Python code.

    Args:
        code: The Python code as a string.

    Returns:
        A list of error messages encountered during validation. If no errors occur, an empty list is returned.
    """
    with TemporaryDirectory() as d:
        try:
            temp_file = Path(d) / APPLICATION_FILE_NAME
            write_file_contents(str(temp_file), code)

            # Import the module using importlib
            spec = importlib.util.spec_from_file_location("tmp_module", temp_file)
            module = importlib.util.module_from_spec(spec) # type: ignore
            spec.loader.exec_module(module) # type: ignore

        except Exception as e:
            return [ f"{type(e).__name__}: {e}"]

        return []

# %% ../../nbs/Helper.ipynb 18
def set_logger_level(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to set the logger level based on verbosity.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.
    """

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs): # type: ignore
        if ("verbose" in kwargs) and kwargs["verbose"]:
            set_level(logging.INFO)
        else:
            set_level(logging.WARNING)
        return func(*args, **kwargs)

    return wrapper_decorator

# %% ../../nbs/Helper.ipynb 21
# Reference: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb


def _retry_with_exponential_backoff(
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    max_wait: float = 60,
    errors: tuple = (
        openai.error.RateLimitError,
        openai.error.ServiceUnavailableError,
        openai.error.APIError,
    ),
) -> Callable:
    """Retry a function with exponential backoff."""

    def decorator(
        func: Callable[[str], Tuple[str, str]]
    ) -> Callable[[str], Tuple[str, str]]:
        def wrapper(*args, **kwargs):  # type: ignore
            num_retries = 0
            delay = initial_delay

            while True:
                try:
                    return func(*args, **kwargs)

                except errors as e:
                    num_retries += 1
                    if num_retries > max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        )
                    delay = min(
                        delay
                        * exponential_base
                        * (1 + jitter * random.random()),  # nosec
                        max_wait,
                    )
                    logger.info(
                        f"Note: OpenAI's API rate limit reached. Command will automatically retry in {int(delay)} seconds. For more information visit: https://help.openai.com/en/articles/5955598-is-api-usage-subject-to-any-rate-limits",
                    )
                    time.sleep(delay)

                except Exception as e:
                    raise e

        return wrapper

    return decorator

# %% ../../nbs/Helper.ipynb 24
def _get_relevant_document(query: str) -> str:
    """Load the vector database and retrieve the most relevant document based on the given query.

    Args:
        query: The query for relevance-based document retrieval.

    Returns:
        The content of the most relevant document as a string.
    """
    db_path = get_root_data_path() / "docs"
    db = FAISS.load_local(db_path, OpenAIEmbeddings()) # type: ignore
    results = db.max_marginal_relevance_search(query, k=1, fetch_k=3)
    results_str = "\n".join([result.page_content for result in results])
    return results_str

# %% ../../nbs/Helper.ipynb 26
examples_delimiter = {
    "skeleton": {
        "start": "==== app_skeleton.py starts ====",
        "end": "==== app_skeleton.py ends ====",
    },
    "app": {
        "start": "==== app.py starts ====",
        "end": "==== app.py ends ====",
    },
    "test_app": {
        "start": "==== test_app.py starts ====",
        "end": "==== test_app.py ends ====",
    },
}


def _split_text(text: str, delimiter: Dict[str, str]) -> str:
    return text.split(delimiter["start"])[-1].split(delimiter["end"])[0]


def _format_examples(parent_docs_str: List[str]) -> Dict[str, str]:
    """Format and extract examples from parent document.

    Args:
        parent_docs_str (List[str]): A list of parent document strings containing example sections.

    Returns:
        Dict[str, List[str]]: A dictionary with sections as keys and lists of formatted examples as values.
    """
    ret_val = {"description_to_skeleton": "", "skeleton_to_app_and_test": ""}
    for d in parent_docs_str:
        description = d.split("==== description.txt starts ====")[-1]
        skeleton = _split_text(d, examples_delimiter["skeleton"])
        app = _split_text(d, examples_delimiter["app"])
        test_app = _split_text(d, examples_delimiter["test_app"])

        ret_val[
            "description_to_skeleton"
        ] += f"\n==== EXAMPLE APP DESCRIPTION ====\n{description}\n\n==== YOUR RESPONSE ====\n\n{skeleton}"
        ret_val[
            "skeleton_to_app_and_test"
        ] += f"\n==== EXAMPLE APP DESCRIPTION ====\n{description}\n\n==== EXAMPLE APP SKELETON ====\n{skeleton}\n==== YOUR RESPONSE ====\n\n### application.py ###\n{app}\n### test.py ###\n{test_app}"

    return ret_val

# %% ../../nbs/Helper.ipynb 28
def get_relevant_prompt_examples(query: str) -> Dict[str, str]:
    """Load the vector database and retrieve the most relevant examples based on the given query for each step.

    Args:
        query: The query for relevance-based document retrieval.

    Returns:
        The dictionary of the most relevant examples for each step.
    """
    db_path = get_root_data_path() / "examples"
    db = FAISS.load_local(db_path, OpenAIEmbeddings()) # type: ignore
    # Retreive relavent chuncks
    results = db.similarity_search(query, k=3, fetch_k=5)
    # Retreive parent documents for every matched chuncks
    parent_docs = [db.similarity_search("==== app_skeleton.py starts ====",filter=dict(source=r.metadata["source"]), k=2) for r in results]
    parent_docs_str = ["\n\n\n".join([d.page_content for d in docs]) for docs in parent_docs]
    prompt_examples = _format_examples(parent_docs_str)
    return prompt_examples

    

# %% ../../nbs/Helper.ipynb 30
class CustomAIChat:
    """Custom class for interacting with OpenAI

    Attributes:
        model: The OpenAI model to use. If not passed, defaults to gpt-3.5-turbo-16k.
        system_prompt: Initial system prompt to the AI model. If not passed, defaults to SYSTEM_PROMPT.
        initial_user_prompt: Initial user prompt to the AI model.
        params: Parameters to use while initiating the OpenAI chat model. DEFAULT_PARAMS used if not provided.
    """

    def __init__(
        self,
        model: str,
        user_prompt: Optional[str] = None,
        params: Dict[str, float] = DEFAULT_PARAMS,
        semantic_search_query: Optional[str] = None,
    ):
        """Instantiates a new CustomAIChat object.

        Args:
            model: The OpenAI model to use. If not passed, defaults to gpt-3.5-turbo-16k.
            user_prompt: The user prompt to the AI model.
            params: Parameters to use while initiating the OpenAI chat model. DEFAULT_PARAMS used if not provided.
            semantic_search_query: A query string to fetch relevant documents from the database
        """
        self.model = model
        self.messages = [
            {"role": role, "content": content}
            for role, content in [
                ("system", SYSTEM_PROMPT),
                ("user", self._get_doc(semantic_search_query)),
                ("user", user_prompt),
            ]
            if content is not None
        ]
        self.params = params

    @staticmethod
    def _get_doc(semantic_search_query: Optional[str] = None) -> str:
        if semantic_search_query is None:
            return ""
        return _get_relevant_document(semantic_search_query)
    
    @_retry_with_exponential_backoff()
    def __call__(self, user_prompt: str) -> Tuple[str, Dict[str, int]]:
        """Call OpenAI API chat completion endpoint and generate a response.

        Args:
            user_prompt: A string containing user's input prompt.

        Returns:
            A tuple with AI's response message content and the total number of tokens used while generating the response.
        """
        self.messages.append(
            {"role": "user", "content": f"{user_prompt}\n==== YOUR RESPONSE ====\n"}
        )
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.params["temperature"],
        )

        return (
            response["choices"][0]["message"]["content"],
            response["usage"],
        )

# %% ../../nbs/Helper.ipynb 34
class ValidateAndFixResponse:
    """Generates and validates response from OpenAI

    Attributes:
        generate: A callable object for generating responses.
        validate: A callable object for validating responses.
        max_attempts: An optional integer specifying the maximum number of attempts to generate and validate a response.
    """

    def __init__(
        self,
        generate: Callable[..., Any],
        validate: Callable[..., Any],
        max_attempts: Optional[int] = MAX_RETRIES,
    ):
        self.generate = generate
        self.validate = validate
        self.max_attempts = max_attempts

    def construct_prompt_with_error_msg(
        self,
        prompt: str,
        response: str,
        errors: str,
    ) -> str:
        """Construct prompt message along with the error message.

        Args:
            prompt: The original prompt string.
            response: The invalid response string from OpenAI.
            errors: The errors which needs to be fixed in the invalid response.

        Returns:
            A string combining the original prompt, invalid response, and the error message.
        """
        prompt_with_errors = (
            prompt
            + f"\n\n==== YOUR RESPONSE (WITH ISSUES) ====\n\n{response}"
            + f"\n\nRead the contents of ==== YOUR RESPONSE (WITH ISSUES) ==== section and fix the below mentioned issues:\n\n{errors}"
        )
        return prompt_with_errors

    def fix(
        self, prompt: str, total_usage: List[Dict[str, int]], **kwargs: str
    ) -> Tuple[str, List[Dict[str, int]]]:
        raise NotImplementedError()

# %% ../../nbs/Helper.ipynb 36
def add_tokens_usage(usage_list: List[Dict[str, int]]) -> Dict[str, int]:
    """Add list of OpenAI "usage" dictionaries by categories defined in TOKEN_TYPES (prompt_tokens, completion_tokens and total_tokens).

    Args:
        usage_list: List of OpenAI "usage" dictionaries


    Returns:
        Dict[str, int]: Dictionary where the keys are TOKEN_TYPES and their values are the sum of OpenAI "usage" dictionaries
    """
    added_tokens: Dict[str, int] = defaultdict(int)
    for usage in usage_list:
        for token_type in TOKEN_TYPES:
            added_tokens[token_type] += usage[token_type]
            
    return added_tokens

# %% ../../nbs/Helper.ipynb 39
@patch  # type: ignore
def fix(
    self: ValidateAndFixResponse, prompt: str, total_usage: List[Dict[str, int]], **kwargs: str
) -> Tuple[str, List[Dict[str, int]]]:
    """Fix the response from OpenAI until no errors remain or maximum number of attempts is reached.

    Args:
        prompt: The initial prompt string.
        kwargs: Additional keyword arguments to be passed to the validation function.


    Returns:
        str: The generated response that has passed the validation.

    Raises:
        ValueError: If the maximum number of attempts is exceeded and the response has not successfully passed the validation.
    """
    iterations = 0
    initial_prompt = prompt
    total_tokens_usage: Dict[str, int] = defaultdict(int)
    try:
        while True:
            response, usage = self.generate(prompt)
            total_tokens_usage = add_tokens_usage([total_tokens_usage, usage])
            errors = self.validate(response, **kwargs)
            if len(errors) == 0:
                total_usage.append(total_tokens_usage)
                return response, total_usage
            error_str = "\n".join(errors)
            prompt = self.construct_prompt_with_error_msg(
                initial_prompt, response, error_str
            )
            logger.info(
                f"Validation failed due to the following errors, trying again...\n{error_str}\n\nBelow is the prompt we are sending on this retry:\n{prompt}"
            )
            iterations += 1
            if self.max_attempts is not None and iterations >= self.max_attempts:
                raise ValueError(
                    f"✘ Error: {MAX_NUM_FIXES_MSG} ({self.max_attempts}) exceeded. Unable to fix the following issues. Please try again...\n{error_str}\n\n{INCOMPLETE_DESCRIPTION}\n{DESCRIPTION_EXAMPLE}\n\n"
                )
    except:
        total_usage.append(total_tokens_usage)
        raise