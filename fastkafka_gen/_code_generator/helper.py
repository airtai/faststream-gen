# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Helper.ipynb.

# %% auto 0
__all__ = ['logger', 'add_dir_to_sys_path', 'write_file_contents', 'read_file_contents', 'validate_python_code',
           'set_logger_level', 'CustomAIChat', 'ValidateAndFixResponse', 'add_tokens_usage']

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

import openai
from fastcore.foundation import patch

from .._components.logger import get_logger, set_level
from .prompts import SYSTEM_PROMPT, DEFAULT_FASTKAFKA_PROMPT
from .constants import DEFAULT_PARAMS, DEFAULT_MODEL, MAX_RETRIES, ASYNC_API_SPEC_FILE_NAME, APPLICATION_FILE_NAME, TOKEN_TYPES

# %% ../../nbs/Helper.ipynb 3
logger = get_logger(__name__)

# %% ../../nbs/Helper.ipynb 5
@contextmanager
def add_dir_to_sys_path(dir_: str) -> Generator[None, None, None]:
    """Add a directory path to sys.path

    Args:
        dir_ : the path to add to sys.path

    Returns:
        None

    Raises:
        ValueError: If dir_ is None
    """
    dir_path = Path(dir_).absolute().resolve(strict=True)
    original_path = sys.path[:]
    sys.path.insert(0, str(dir_path))
    try:
        yield
    finally:
        sys.path = original_path

# %% ../../nbs/Helper.ipynb 7
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

# %% ../../nbs/Helper.ipynb 9
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

# %% ../../nbs/Helper.ipynb 12
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

# %% ../../nbs/Helper.ipynb 16
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

# %% ../../nbs/Helper.ipynb 19
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

# %% ../../nbs/Helper.ipynb 22
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
        model: Optional[str] = DEFAULT_MODEL,
        user_prompt: Optional[str] = None,
        params: Dict[str, float] = DEFAULT_PARAMS,
    ):
        """Instantiates a new CustomAIChat object.

        Args:
            model: The OpenAI model to use. If not passed, defaults to gpt-3.5-turbo-16k.
            user_prompt: The user prompt to the AI model.
            params: Parameters to use while initiating the OpenAI chat model. DEFAULT_PARAMS used if not provided.
        """
        self.model = model
        self.messages = [
            {"role": role, "content": content}
            for role, content in [
                ("system", SYSTEM_PROMPT),
                ("user", DEFAULT_FASTKAFKA_PROMPT),
                ("user", user_prompt),
            ]
            if content is not None
        ]
        self.params = params

    @_retry_with_exponential_backoff()
    def __call__(self, user_prompt: str) -> Tuple[str, Dict[str, int]]:
        """Call OpenAI API chat completion endpoint and generate a response.

        Args:
            user_prompt: A string containing user's input prompt.

        Returns:
            A tuple with AI's response message content and the total number of tokens used while generating the response.
        """
        self.messages.append(
            {"role": "user", "content": f"==== APP DESCRIPTION: ====\n\n{user_prompt}"}
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

# %% ../../nbs/Helper.ipynb 26
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
            + f"\n\n==== RESPONSE WITH ISSUES ====\n\n{response}"
            + f"\n\nRead the contents of ==== RESPONSE WITH ISSUES ==== section and fix the below mentioned issues:\n\n{errors}"
        )
        return prompt_with_errors

    def fix(
        self, prompt: str, use_prompt_in_validation: bool = False
    ) -> Tuple[str, Dict[str, int]]:
        raise NotImplementedError()

# %% ../../nbs/Helper.ipynb 28
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

# %% ../../nbs/Helper.ipynb 31
@patch  # type: ignore
def fix(
    self: ValidateAndFixResponse, prompt: str, use_prompt_in_validation: bool = False
) -> Tuple[str, Dict[str, int]]:
    """Fix the response from OpenAI until no errors remain or maximum number of attempts is reached.

    Args:
        prompt: The initial prompt string.
        use_prompt_in_validation: Flag indicating whether to use the prompt while validating the generated response. This will be useful
            while validating the test code. Because the tests will run against the app code.


    Returns:
        str: The generated response that has passed the validation.

    Raises:
        ValueError: If the maximum number of attempts is exceeded and the response has not successfully passed the validation.
    """
    iterations = 0
    initial_prompt = prompt
    total_tokens_usage: Dict[str, int] = defaultdict(int)
    while True:
        response, usage = self.generate(prompt)
        total_tokens_usage = add_tokens_usage([total_tokens_usage, usage])
        errors = (
            self.validate(response, prompt)
            if use_prompt_in_validation
            else self.validate(response)
        )
        if len(errors) == 0:
            return response, total_tokens_usage
        error_str = "\n".join(errors)
        logger.info(
            f"Validation failed due to the following errors, trying again...\n{error_str}\n\nBelow is the invalid response with the mentioned errors:\n\n{response}\n\n"
        )
        prompt = self.construct_prompt_with_error_msg(
            initial_prompt, response, error_str
        )
        iterations += 1
        if self.max_attempts is not None and iterations >= self.max_attempts:
            raise ValueError(
                f"Maximum number of retries ({self.max_attempts}) exceeded. Unable to fix the following issues. Please try again...\n{error_str}\n\n"
            )
