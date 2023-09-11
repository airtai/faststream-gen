# Code generator for FastStream

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

The faststream-gen library uses advanced AI to generate `FastStream`
code from the application description, speeding up `FastStream` app
development.

------------------------------------------------------------------------

![PyPI](https://img.shields.io/pypi/v/faststream-gen.png) ![PyPI -
Downloads](https://img.shields.io/pypi/dm/faststream-gen.png) ![PyPI -
Python
Version](https://img.shields.io/pypi/pyversions/faststream-gen.png)

![GitHub Workflow
Status](https://img.shields.io/github/actions/workflow/status/airtai/fastkafka-gen/test.yaml)
![GitHub](https://img.shields.io/github/license/airtai/fastkafka-gen.png)

------------------------------------------------------------------------

If you’ve heard of the `FastStream` library and wanted to try it but
didn’t have time to read the documentation, no worries! `faststream-gen`
will generate FastStream applications for you automatically.

It not only creates your FastStream application, but it also generates
the necessary tests to ensure its functionality. Simply describe your
application in english, and faststream-gen will take care of the rest.

## Install

faststream-gen is published as a Python package and can be installed
with pip:

``` sh
pip install faststream-gen
```

If the installation was successful, you should now have the
faststream-gen installed on your system. Run the below command from the
terminal to see the full list of available options:

``` sh
faststream_gen --help
```

                                                                                    
     Usage: faststream_gen [OPTIONS] [DESCRIPTION]                                  
                                                                                    
     Effortlessly generate FastStream application code and integration tests from   
     the app description.                                                           
                                                                                    
    ╭─ Arguments ──────────────────────────────────────────────────────────────────╮
    │   description      [DESCRIPTION]  Summarize your FastStream app in a few     │
    │                                   sentences!                                 │
    │                                                                              │
    │                                   Include details about messages, topics,    │
    │                                   servers, and a brief overview of the       │
    │                                   intended business logic.                   │
    │                                                                              │
    │                                   The simpler and more specific the app      │
    │                                   description is, the better the generated   │
    │                                   app will be. Please refer to the below     │
    │                                   example for inspiration:                   │
    │                                                                              │
    │                                   Create a FastStream application using      │
    │                                   localhost broker for testing and use the   │
    │                                   default port number.  It should consume    │
    │                                   messages from the "input_data" topic,      │
    │                                   where each message is a JSON encoded       │
    │                                   object containing a single attribute:      │
    │                                   'data'.  For each consumed message, create │
    │                                   a new message object and increment the     │
    │                                   value of the data attribute by 1. Finally, │
    │                                   send the modified message to the           │
    │                                   'output_data' topic.                       │
    │                                   [default: None]                            │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Options ────────────────────────────────────────────────────────────────────╮
    │ --input_file          -i      TEXT  The path to the file with the app        │
    │                                     desription. This path should be relative │
    │                                     to the current working directory.        │
    │                                     If the app description is passed via     │
    │                                     both a --input_file and a command line   │
    │                                     argument, the description from the       │
    │                                     command line will be used to create the  │
    │                                     application.                             │
    │                                     [default: None]                          │
    │ --output_path         -o      TEXT  The path to the output directory where   │
    │                                     the generated files will be saved. This  │
    │                                     path should be relative to the current   │
    │                                     working directory.                       │
    │                                     [default: ./faststream-gen]              │
    │ --verbose             -v            Enable verbose logging by setting the    │
    │                                     logger level to INFO.                    │
    │ --install-completion                Install completion for the current       │
    │                                     shell.                                   │
    │ --show-completion                   Show completion for the current shell,   │
    │                                     to copy it or customize the              │
    │                                     installation.                            │
    │ --help                              Show this message and exit.              │
    ╰──────────────────────────────────────────────────────────────────────────────╯

## How to use

### Setup

For generating `FastStream` applications, `faststream-gen` is using
`OPENAI` models. So the first step is exporting your `OPENAI_API_KEY`.

``` sh
export OPENAI_API_KEY="<your_openai_api_key>"
```

If you don’t already have `OPENAI_API_KEY`, you can create one at
[OPENAI API keys](https://platform.openai.com/account/api-keys)

### Code generation

This library is very easy to use. The only thing you need to do is
prepare a description of your `FastStream` application, i.e. write what
your application should do and pass it to the `faststream_gen` command
as a string:

``` sh
faststream_gen "<your_app_description>"
```

#### Example

``` sh
faststream_gen  "Write a faststream application with with one consumer function and two producer functions. The consumer function should receive the a message posted on 'new_joinee' topic. The message should contain 'employee_name', 'age', 'location' and 'experience' attributes. After consuming the consumer function should send the details to the 'project_team' and 'admin_team' topics. Use only localhost broker" 
✨  Generating a new FastStream application!
 ✔ Application description validated 
 ✔ FastStream app skeleton generated and saved at: ./faststream-gen/application_skeleton.py 
 ✔ FastStream app generated and saved at: ./faststream-gen/application.py 
 ✔ Tests are generated and saved at: ./faststream-gen/test.py 
 Tokens used: 18572
 Total Cost (USD): $0.05635
✨  All files were successfully generated!
```

**Note**: If you have longer application description (and we encourage
writing a detailed description), it is easier to save description into
the file and use:

``` sh
faststream_gen -i <path_to_app_description.txt>
```

The `faststream_gen` CLI command will create `faststream-gen` folder
(you can set different output folder by providing `--output_path` option
in the CLI) and save generated FastStream `application.py` inside the
folder. We know that no one likes code full of errors, that’s why
`faststream_gen` generates and run tests along with the generated
application!

Next to `application.py` you will find the `test.py` script for testing
your FastStream application!

In the `faststream-gen` folder you will find following files:

`application.py`

``` python
from pydantic import BaseModel, Field

from faststream import FastStream, Logger
from faststream.kafka import KafkaBroker


class Employee(BaseModel):
    employee_name: str = Field(
        ..., examples=["John Doe"], description="Employee name"
    )
    age: int = Field(
        ..., examples=[30], description="Age"
    )
    location: str = Field(
        ..., examples=["New York"], description="Location"
    )
    experience: int = Field(
        ..., examples=[5], description="Experience in years"
    )


broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


@broker.subscriber("new_joinee")
@broker.publisher("project_team")
@broker.publisher("admin_team")
async def on_new_joinee(msg: Employee, logger: Logger):
    logger.info(msg)
    return msg
```

`test.py`

``` python
import pytest

from faststream.kafka import TestKafkaBroker

from application import *


@broker.subscriber("project_team")
async def on_project_team(msg: Employee):
    pass

@broker.subscriber("admin_team")
async def on_admin_team(msg: Employee):
    pass

@pytest.mark.asyncio
async def test_app():
    async with TestKafkaBroker(broker):
        await broker.publish(Employee(employee_name="John Doe", age=30, location="New York", experience=5), "new_joinee")

        on_new_joinee.mock.assert_called_with(dict(Employee(employee_name="John Doe", age=30, location="New York", experience=5)))
        on_project_team.mock.assert_called_with(dict(Employee(employee_name="John Doe", age=30, location="New York", experience=5)))
        on_admin_team.mock.assert_called_with(dict(Employee(employee_name="John Doe", age=30, location="New York", experience=5)))
```

Finally, you can personally check whether all the generated tests pass:

``` sh
pytest faststream-gen/test.py
```

## Copyright

Copyright © 2023 onwards airt technologies ltd, Inc.

## License

This project is licensed under the terms of the
<a href="https://github.com/airtai/fastkafka-gen/blob/main/LICENSE" target="_blank">Apache
License 2.0</a>
