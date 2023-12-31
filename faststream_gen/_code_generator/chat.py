# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Chat.ipynb.

# %% auto 0
__all__ = ['logger', 'CustomAIChat', 'ValidateAndFixResponse']

# %% ../../nbs/Chat.ipynb 1
from typing import *
import random
import logging
import time
from collections import defaultdict
from pathlib import Path

import openai
from fastcore.foundation import patch
from langchain.schema.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from faststream_gen._code_generator.constants import (
    DEFAULT_PARAMS,
    MAX_RETRIES,
    STEP_LOG_DIR_NAMES,
    MAX_NUM_FIXES_MSG,
    INCOMPLETE_DESCRIPTION,
    DESCRIPTION_EXAMPLE,
    LOGS_DIR_NAME,
)
from .._components.logger import get_logger, set_level
from .prompts import SYSTEM_PROMPT
from .helper import add_tokens_usage
from .._components.package_data import get_root_data_path

# %% ../../nbs/Chat.ipynb 3
logger = get_logger(__name__, level=logging.WARNING)

# %% ../../nbs/Chat.ipynb 5
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

# %% ../../nbs/Chat.ipynb 8
def _get_relevant_document(query: str) -> str:
    """Load the vector database and retrieve the most relevant document based on the given query.

    Args:
        query: The query for relevance-based document retrieval.

    Returns:
        The content of the most relevant document as a string.
    """
    db_path = get_root_data_path() / "docs"
    db = FAISS.load_local(db_path, OpenAIEmbeddings())
    results = db.max_marginal_relevance_search(query, k=1, fetch_k=3)
    results_str = "\n".join([result.page_content for result in results])
    return results_str

# %% ../../nbs/Chat.ipynb 10
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
        prompt_str = "\n\n".join([f"===Role:{m['role']}===\n\nMessage:\n{m['content']}" for m in self.messages])
        logger.info(f"\n\nPrompt to the model: \n\n{prompt_str}")
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.params["temperature"],
        )

        return (
            response["choices"][0]["message"]["content"],
            response["usage"],
        )

# %% ../../nbs/Chat.ipynb 12
class ValidateAndFixResponse:
    """Generates and validates response from OpenAI

    Attributes:
        generate: A callable object for generating responses.
        validate: A callable object for validating responses.
        max_retries: An optional integer specifying the maximum number of attempts to generate and validate a response.
    """

    def __init__(
        self,
        generate: Callable[..., Any],
        validate: Callable[..., Any],
        max_retries: Optional[int] = MAX_RETRIES,
    ):
        self.generate = generate
        self.validate = validate
        self.max_retries = max_retries

    def fix(
        self,
        prompt: str,
        total_usage: List[Dict[str, int]],
        step_name: Optional[str] = None,
        log_dir_path: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> Tuple[str, List[Dict[str, int]]]:
        raise NotImplementedError()

# %% ../../nbs/Chat.ipynb 13
def _save_log_results(
    step_name: str,
    log_dir_path: str,
    messages: List[Dict[str, str]],
    response: str,
    error_str: str,
    retry_cnt: int,
    **kwargs: Dict[str, int],
) -> None:
    if log_dir_path is not None and "attempt" in kwargs:
        step_dir = Path(log_dir_path) / step_name
        step_dir.mkdir(parents=True, exist_ok=True)

        attempt_dir = step_dir / f'attempt_{kwargs["attempt"] + 1}'  # type: ignore
        attempt_dir.mkdir(parents=True, exist_ok=True)

        try_dir = attempt_dir / f"try_{retry_cnt+1}"
        try_dir.mkdir(parents=True, exist_ok=True)

        formatted_msg = "\n".join(
            [f"===={m['role']}====\n\n{m['content']}\n\n" for m in messages]
        )

        with open((try_dir / "input.txt"), "w", encoding="utf-8") as f_input, open(
            (try_dir / "output.txt"), "w", encoding="utf-8"
        ) as f_output, open(
            (try_dir / "errors.txt"), "w", encoding="utf-8"
        ) as f_errors:
            f_input.write(formatted_msg)
            f_output.write(response)
            f_errors.write(error_str)

# %% ../../nbs/Chat.ipynb 15
def _construct_prompt_with_error_msg(
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
        f"\n\n==== YOUR RESPONSE (WITH ISSUES) ====\n\n{response}"
        + f"\n\nRead the contents of ==== YOUR RESPONSE (WITH ISSUES) ==== section and fix the below mentioned issues:\n\n{errors}"
    )
    return prompt_with_errors

# %% ../../nbs/Chat.ipynb 17
@patch  # type: ignore
def fix(
    self: ValidateAndFixResponse,
    prompt: str,
    total_usage: List[Dict[str, int]],
    step_name: str,
    output_directory: str,
    **kwargs: Dict[str, Any],
) -> List[Dict[str, int]]:
    """Fix the response from OpenAI until no errors remain or maximum number of attempts is reached.

    Args:
        prompt: The initial prompt string.
        kwargs: Additional keyword arguments to be passed to the validation function.

    Returns:
        str: The generated response that has passed the validation.

    Raises:
        ValueError: If the maximum number of attempts is exceeded and the response has not successfully passed the validation.
    """
    total_tokens_usage: Dict[str, int] = defaultdict(int)
    log_dir_path = Path(output_directory) / LOGS_DIR_NAME
    for i in range(self.max_retries):  # type: ignore
        response, usage = self.generate(prompt)
        total_tokens_usage = add_tokens_usage([total_tokens_usage, usage])
        
        if step_name == STEP_LOG_DIR_NAMES["app"]:
            errors, response = self.validate(response, output_directory, **kwargs)
        else:
            errors = self.validate(response, output_directory, **kwargs)
        error_str = "\n".join(errors)
        _save_log_results(
            step_name,
            str(log_dir_path),
            self.generate.messages,  # type: ignore
            response,
            error_str,
            i,
            **kwargs,
        )
        if len(errors) == 0:
            total_usage.append(total_tokens_usage)
            return total_usage

        self.generate.messages[-1]["content"] = self.generate.messages[-1][ # type: ignore
            "content"
        ].rsplit("==== YOUR RESPONSE ====", 1)[0]
        prompt = _construct_prompt_with_error_msg(response, error_str)
        logger.info(f"Validation failed, trying again...Errors:\n{error_str}")

    total_usage.append(total_tokens_usage)
    
    # we send False to notify the generated code contains bugs
    raise ValueError(total_usage, False)
