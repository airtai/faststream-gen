# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Constants.ipynb.

# %% auto 0
__all__ = ['DESCRIPTION_FILE_NAME', 'APPLICATION_SKELETON_FILE_NAME', 'ASYNC_API_SPEC_FILE_NAME', 'APPLICATION_FILE_NAME',
           'INTEGRATION_TEST_FILE_NAME', 'INTERMEDIATE_RESULTS_DIR_NAME', 'GENERATE_APP_FROM_ASYNCAPI',
           'GENERATE_APP_FROM_SKELETON', 'GENERATE_APP_SKELETON', 'DEFAULT_PARAMS', 'DEFAULT_MODEL', 'MAX_RETRIES',
           'MAX_ASYNC_SPEC_RETRIES', 'TOKEN_TYPES', 'MODEL_PRICING', 'INCOMPLETE_DESCRIPTION', 'DESCRIPTION_EXAMPLE',
           'MAX_NUM_FIXES_MSG', 'FASTSTREAM_REPO_ZIP_URL', 'FASTSTREAM_DOCS_DIR_SUFFIX',
           'FASTSTREAM_EXAMPLES_DIR_SUFFIX', 'FASTSTREAM_EXAMPLE_FILES', 'FASTSTREAM_TMP_DIR_PREFIX',
           'FASTSTREAM_DIR_TO_EXCLUDE']

# %% ../../nbs/Constants.ipynb 2
DESCRIPTION_FILE_NAME = "app_description.txt"
APPLICATION_SKELETON_FILE_NAME = "application_skeleton.py"
ASYNC_API_SPEC_FILE_NAME = "asyncapi.yml"
APPLICATION_FILE_NAME = "application.py"
INTEGRATION_TEST_FILE_NAME = "test.py"
INTERMEDIATE_RESULTS_DIR_NAME = "intermediate_results"

GENERATE_APP_FROM_ASYNCAPI = "generate_app_from_asyncapi"
GENERATE_APP_FROM_SKELETON = "generate_app_from_skeleton"
GENERATE_APP_SKELETON = "generate_app_skeleton"

# %% ../../nbs/Constants.ipynb 4
DEFAULT_PARAMS = {
    "temperature": 0.7,
}

DEFAULT_MODEL = "gpt-3.5-turbo-16k" # gpt-3.5-turbo

MAX_RETRIES = 5
MAX_ASYNC_SPEC_RETRIES = 3

# %% ../../nbs/Constants.ipynb 6
TOKEN_TYPES = ["prompt_tokens", "completion_tokens", "total_tokens"]

MODEL_PRICING = {
    "gpt-4-32k": {
        "input": 0.06,
        "output": 0.12
    },
    "gpt-3.5-turbo-16k": {
        "input": 0.003,
        "output": 0.004
    },
}

# %% ../../nbs/Constants.ipynb 8
INCOMPLETE_DESCRIPTION = "Please check if your application description is missing some crutial information:\n - Description of the messages which will be produced/consumed\n - At least one topic\n - The business logic to implement while consuming/producing the messages\n"
DESCRIPTION_EXAMPLE = """
If you're unsure about how to construct the app description, consider the following example for guidance

APPLICATION DESCRIPTION EXAMPLE:
Create a FastStream application using localhost broker for testing and use the default port number. 
It should consume messages from the "input_data" topic, where each message is a JSON encoded object containing a single attribute: 'data'. 
For each consumed message, create a new message object and increment the value of the data attribute by 1. Finally, send the modified message to the 'output_data' topic.
"""

MAX_NUM_FIXES_MSG = "Maximum number of retries"

# %% ../../nbs/Constants.ipynb 10
FASTSTREAM_REPO_ZIP_URL = "http://github.com/airtai/fastkafka/archive/FastStream.zip"
FASTSTREAM_DOCS_DIR_SUFFIX = "fastkafka-FastStream/.faststream_gen"
FASTSTREAM_EXAMPLES_DIR_SUFFIX = "fastkafka-FastStream/faststream_gen_examples"
FASTSTREAM_EXAMPLE_FILES = ['description.txt', 'app_skeleton.py', 'app.py', 'test_app.py']
FASTSTREAM_TMP_DIR_PREFIX = "appended_examples"
FASTSTREAM_DIR_TO_EXCLUDE = "api"
