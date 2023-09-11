# Release notes

<!-- do not remove -->

## 0.0.1.dev20230911

### New Features

- Move hardcoded examples in the prompt into a vector database ([#71](https://github.com/airtai/faststream-gen/pull/71)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #63

- Integrate new library and test ([#66](https://github.com/airtai/faststream-gen/pull/66)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #64

- Retrieve relevant embeddings and add it to prompt ([#65](https://github.com/airtai/faststream-gen/pull/65)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #58

- Generate embeddings for guides and the index page and store them in the package data directory ([#61](https://github.com/airtai/faststream-gen/pull/61)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #57

- Generate embeddings for guides and the index page, and store them in the package_data ([#57](https://github.com/airtai/faststream-gen/issues/57))

- Add a new --version option to the fastkafka_gen CLI command to display the code generator's FastKafka version. ([#55](https://github.com/airtai/faststream-gen/issues/55))
  - Expected CLI command:

fastkafka_gen --version

Expected output:

Display the code generator's version as well as the FastKafka version that was used to generate the code.

fastkafka_gen        0.0.1
fastkafka                0.8.0

Reference:

https://typer.tiangolo.com/tutorial/options/version/
https://github.com/tiangolo/typer/issues/52

- Validate the generated test code against the application code and auto fix the errors ([#53](https://github.com/airtai/faststream-gen/pull/53)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #33

- Update test generation prompt ([#43](https://github.com/airtai/faststream-gen/pull/43)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #42

- Show the approximate cost in dollars on the console, similar to how the langchain library does. ([#40](https://github.com/airtai/faststream-gen/issues/40))
  - Current Implementation:

▶ Total tokens usage: 2132
 🤑 Total price: 0.0064💲


Langchain Implementation:

Tokens Used: 42
        Prompt Tokens: 4
        Completion Tokens: 38
Total Cost (USD): $0.00084

Reference: https://python.langchain.com/docs/modules/model_io/models/llms/token_usage_tracking

- Show token usage and provide an estimated cost (in $), even if the CLI command terminates due to an error. ([#38](https://github.com/airtai/faststream-gen/issues/38))

- Generate test code for the generated application code ([#32](https://github.com/airtai/faststream-gen/pull/32)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #6

- Generate application code based on the asyncapi spec ([#28](https://github.com/airtai/faststream-gen/pull/28)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)
  - Closes #7

### Bugs Squashed

- Update the app_creation prompt to fix the error mentioned in the description ([#36](https://github.com/airtai/faststream-gen/issues/36))
  - Error: PydanticUserError: `regex` is removed. use `pattern` instead

Description: The model uses old syntax of pydantic for declaring the field types.

Fix: Instruct the model to use the latest syntax while creating the Field instance in the prompt. Refer to the below example

Current implementation: currency: str = Field(..., description="Currency of the product.", regex="^[A-Z]{3}$")
Expected implementation: currency: str = Field(..., description="Currency of the product.", pattern="^[A-Z]{3}$")

