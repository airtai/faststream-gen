# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/App_Skeleton_Generator.ipynb.

# %% auto 0
__all__ = ['logger', 'generate_app_skeleton']

# %% ../../nbs/App_Skeleton_Generator.ipynb 1
from typing import *
import time
import json
from pathlib import Path

from yaspin import yaspin

from .._components.logger import get_logger
from faststream_gen._code_generator.helper import (
    CustomAIChat,
    ValidateAndFixResponse,
    write_file_contents,
    read_file_contents,
    validate_python_code,
    retry_on_error,
)
from .prompts import APP_SKELETON_GENERATION_PROMPT
from faststream_gen._code_generator.constants import (
    DESCRIPTION_FILE_NAME,
    APPLICATION_SKELETON_FILE_NAME,
    GENERATE_APP_SKELETON,
)

# %% ../../nbs/App_Skeleton_Generator.ipynb 3
logger = get_logger(__name__)

# %% ../../nbs/App_Skeleton_Generator.ipynb 5
@retry_on_error() # type: ignore
def _generate(
    model: str,
    prompt: str,
    app_description_content: str,
    total_usage: List[Dict[str, int]],
) -> Tuple[str, List[Dict[str, int]]]:
    app_generator = CustomAIChat(
        params={
            "temperature": 0.2,
        },
        model=model,
        user_prompt=prompt,
        #             semantic_search_query=app_description_content,
    )
    app_validator = ValidateAndFixResponse(app_generator, validate_python_code)
    return app_validator.fix(app_description_content, total_usage)


def generate_app_skeleton(
    code_gen_directory: str,
    model: str,
    total_usage: List[Dict[str, int]],
    relevant_prompt_examples: str,
) -> List[Dict[str, int]]:
    """Generate skeleton code for the new FastStream app from the application description

    Args:
        code_gen_directory: The directory containing the generated files.
        total_usage: list of token usage.
        relevant_prompt_examples: Relevant examples to add in the prompts.

    Returns:
        The total token used to generate the FastStream code
    """
    logger.info("==== Description to Skeleton Generation ====")
    with yaspin(
        text=f"Generating FastStream app skeleton code (usually takes around 15 to 30 seconds)...",
        color="cyan",
        spinner="clock",
    ) as sp:
        app_description_file_name = f"{code_gen_directory}/{DESCRIPTION_FILE_NAME}"
        app_description_content = read_file_contents(app_description_file_name)

        prompt = APP_SKELETON_GENERATION_PROMPT.replace(
            "==== RELEVANT EXAMPLES GOES HERE ====", f"\n{relevant_prompt_examples}"
        )

        validated_app, total_usage = _generate(
            model, prompt, app_description_content, total_usage
        )

        output_file = f"{code_gen_directory}/{APPLICATION_SKELETON_FILE_NAME}"
        write_file_contents(output_file, validated_app)

        sp.text = ""
        sp.ok(f" ✔ FastStream app skeleton code generated.")
        return total_usage
