# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Prompts.ipynb.

# %% auto 0
__all__ = ['SYSTEM_PROMPT', 'APP_VALIDATION_PROMPT', 'ASYNCAPI_SPEC_GENERATION_PROMPT', 'APP_SKELETON_GENERATION_PROMPT',
           'APP_AND_TEST_GENERATION_PROMPT', 'REQUIREMENTS_GENERATION_PROMPT']

# %% ../../nbs/Prompts.ipynb 1
SYSTEM_PROMPT = """
You are an expert Python developer, tasked to generate executable Python code as a part of your work with the FastStream framework. 

You are to abide by the following guidelines:

1. You must never enclose the generated Python code with ``` python. It is mandatory that the output is a valid and executable Python code. Please ensure this rule is never broken.

2. Some prompts might require you to generate code that contains async functions. For example:

async def app_setup(context: ContextRepo):
    raise NotImplementedError()

In such cases, it is necessary to add the "import asyncio" statement at the top of the code. 

You will encounter sections marked as:

==== APP DESCRIPTION: ====

These sections contain the description of the FastStream app you need to implement. Treat everything below this line, until the end of the prompt, as the description to follow for the app implementation.
"""

# %% ../../nbs/Prompts.ipynb 2
APP_VALIDATION_PROMPT = """
You should provide a response of 0, 1, 2, or 3, and nothing else, based on the following rules:

==== RULES: ====

If the ==== APP DESCRIPTION: ==== section is not related to FastStream or contains violence, self-harm, harassment/threatening, or hate/threatening information, respond with 0.

If the ==== APP DESCRIPTION: ==== section is related to FastStream but primarily provides general information about FastStream and what it is, respond with 1.

If it is NOT possible to infer the topic name or there is no explanation about the business logic in the ==== APP DESCRIPTION: ==== section, respond with 2. This is crucial.

If the ==== APP DESCRIPTION: ==== section is related to FastStream, provides instructions on which topic the messages should be consumed/produced, and includes at least one defined topic, respond with 3.

Here are few examples for your understanding:


==== EXAMPLE APP DESCRIPTION ====
Generate a new FastStream app, which has a producer function and a consumer function 
==== YOUR RESPONSE ====
2

==== EXAMPLE APP DESCRIPTION ====
In App description 1, the user has not defined the message structure or the topic name to publish/subscribe. As a result, you should respond with 2. 
==== YOUR RESPONSE ====
2

==== EXAMPLE APP DESCRIPTION ====
Create a FastStream application.
==== YOUR RESPONSE ====
2

==== EXAMPLE APP DESCRIPTION ====
create FastStream app where message has user_data attribute.
==== YOUR RESPONSE ====
2

==== EXAMPLE APP DESCRIPTION ====
FastStream app with for consuming messages from the hello topic
==== YOUR RESPONSE ====
3

==== EXAMPLE APP DESCRIPTION ====
Write a FastStream application with with one consumer function and two producer functions. The consumer function should receive the a message posted on "new_joinee" topic. The message should contain "employee_name", "age", "location" and "experience" attributes. After consuming the consumer function should send the details to the "project_team" and "admin_team" topics. Use only localhost broker==== Response 5 ====
==== YOUR RESPONSE ====
3

==== EXAMPLE APP DESCRIPTION ====
Develop a new FastStream application that consumes JSON-encoded objects from the "receive_order" topic. These objects include attributes like "name" and "quantity." Upon consumption, enhance the message by adding a "location" attribute set to "Zagreb." Subsequently, forward the modified message to the "place_order" topic. After this, send another message to the "update_inventory" topic. This message should include a "quantity" attribute that corresponds to the received quantity value. No authentication is required.==== Response 6 ====
==== YOUR RESPONSE ====
3

==== EXAMPLE APP DESCRIPTION ====
Who are you
==== YOUR RESPONSE ====
0

==== EXAMPLE APP DESCRIPTION ====
What is the latest vesion of FastStream
==== YOUR RESPONSE ====
1

Please respond only with numbers 0, 1, 2 or 3 (WITH NO ADDITIONAL TEXT!)

==== APP DESCRIPTION: ====

"""

# %% ../../nbs/Prompts.ipynb 3
ASYNCAPI_SPEC_GENERATION_PROMPT = """
Generate an AsyncAPI specification using the content from "APP DESCRIPTION" section. Follow the example patterns provided for reference.

==== EXAMPLE APP DESCRIPTION ====

Create a FastStream application using localhost broker for testing and use the default port number. It should consume messages from the "input_data" topic, where each message is a JSON encoded object containing a single attribute: 'data'. For each consumed message, create a new message object and increment the value of the data attribute by 1. Finally, send the modified message to the 'output_data' topic.

==== YOUR RESPONSE ====

asyncapi: 2.6.0
defaultContentType: application/json
info:
  title: FastStream
  version: 0.1.0
  description: "A FastKafka application is configured to use a localhost broker for testing, utilizing the default port number. This application is designed to consume messages from the 'input_data' topic, where each message takes the form of a JSON encoded object with a single attribute called 'data'. For every message it consumes, the application creates a new message object and increments the value of the 'data' attribute by 1. Subsequently, it forwards the modified message to the 'output_data' topic."
servers:
  development:
    url: localhost:9092
    protocol: kafka
    protocolVersion: auto
channels:
  OnInputData:
    servers:
    - development
    bindings:
      kafka:
        topic: input_data
        bindingVersion: 0.4.0
    subscribe:
      message:
        $ref: '#/components/messages/OnInputDataMessage'
  Output_DataPublisher:
    servers:
    - development
    bindings:
      kafka:
        topic: output_data
        bindingVersion: 0.4.0
    publish:
      message:
        $ref: '#/components/messages/Output_DataPublisherMessage'
components:
  messages:
    OnInputDataMessage:
      title: OnInputDataMessage
      correlationId:
        location: $message.header#/correlation_id
      payload:
        $ref: '#/components/schemas/DataBasic'
    Output_DataPublisherMessage:
      title: Output_DataPublisherMessage
      correlationId:
        location: $message.header#/correlation_id
      payload:
        $ref: '#/components/schemas/DataBasic'
  schemas:
    DataBasic:
      properties:
        data:
          description: Float data example
          examples:
          - 0.5
          minimum: 0
          title: Data
          type: number
      required:
      - data
      title: DataBasic
      type: object


==== EXAMPLE APP DESCRIPTION ====

Develop a FastStream application using localhost broker for testing. It should consume messages from 'course_updates' topic where the message is a JSON encoded object including two attributes: course_name and new_content. If new_content attribute is set, then construct a new message appending 'Updated: ' before the course_name attribute. Finally, publish this message to the 'notify_updates' topic.


==== YOUR RESPONSE ====

asyncapi: 2.6.0
defaultContentType: application/json
info:
  title: FastStream
  version: 0.1.0
  description: "A FastKafka application using a localhost broker for testing purposes is developed. This application focuses on consuming messages from the 'course_updates' topic, with each message being a JSON-encoded object featuring two attributes: 'course_name' and 'new_content'. The application's key functionality involves checking if the 'new_content' attribute is set in the consumed message. If it is, a new message is generated by appending 'Updated: ' to the 'course_name' attribute. The final step is to publish this modified or original message to the 'notify_updates' topic."
servers:
  development:
    url: localhost:9092
    protocol: kafka
    protocolVersion: auto
channels:
  OnCourseUpdateCourseUpdates:
    servers:
    - development
    bindings:
      kafka:
        topic: course_updates
        bindingVersion: 0.4.0
    subscribe:
      message:
        $ref: '#/components/messages/OnCourseUpdateCourseUpdatesMessage'
  Notify_UpdatePublisher:
    servers:
    - development
    bindings:
      kafka:
        topic: notify_update
        bindingVersion: 0.4.0
    publish:
      message:
        $ref: '#/components/messages/Notify_UpdatePublisherMessage'
components:
  messages:
    OnCourseUpdateCourseUpdatesMessage:
      title: OnCourseUpdateCourseUpdatesMessage
      correlationId:
        location: $message.header#/correlation_id
      payload:
        $ref: '#/components/schemas/CourseUpdates'
    Notify_UpdatePublisherMessage:
      title: Notify_UpdatePublisherMessage
      correlationId:
        location: $message.header#/correlation_id
      payload:
        $ref: '#/components/schemas/CourseUpdates'
  schemas:
    CourseUpdates:
      properties:
        course_name:
          description: Course example
          examples:
          - Biology
          title: Course Name
          type: string
        new_content:
          anyOf:
          - type: string
          - type: 'null'
          default: null
          description: Content example
          examples:
          - New content
          title: New Content
      required:
      - course_name
      title: CourseUpdates
      type: object



==== EXAMPLE APP DESCRIPTION ====

Create a FastStream application using localhost broker. Consume from the 'new_pet' topic, which includes JSON encoded object with attributes: pet_id, species, and age. 
Whenever a new pet is added, send the new pet's information to the 'notify_adopters' topic.


==== YOUR RESPONSE ====

asyncapi: 2.6.0
defaultContentType: application/json
info:
  title: FastStream
  version: 0.1.0
  description: "A FastStream application is established, utilizing a localhost broker. It is designed to consume messages from the 'new_pet' topic, with each message taking the form of a JSON-encoded object encompassing three attributes: 'pet_id,' 'species,' and 'age.' The primary function of this application is to ensure that whenever a new pet is added, its information is sent to the 'notify_adopters' topic."
servers:
  development:
    url: localhost:9092
    protocol: kafka
    protocolVersion: auto
channels:
  OnNewPet:
    servers:
    - development
    bindings:
      kafka:
        topic: new_pet
        bindingVersion: 0.4.0
    subscribe:
      message:
        $ref: '#/components/messages/OnNewPetMessage'
  Notify_AdoptersPublisher:
    servers:
    - development
    bindings:
      kafka:
        topic: notify_adopters
        bindingVersion: 0.4.0
    publish:
      message:
        $ref: '#/components/messages/Notify_AdoptersPublisherMessage'
components:
  messages:
    OnNewPetMessage:
      title: OnNewPetMessage
      correlationId:
        location: $message.header#/correlation_id
      payload:
        $ref: '#/components/schemas/Pet'
    Notify_AdoptersPublisherMessage:
      title: Notify_AdoptersPublisherMessage
      correlationId:
        location: $message.header#/correlation_id
      payload:
        $ref: '#/components/schemas/Pet'
  schemas:
    Pet:
      properties:
        pet_id:
          description: Int data example
          examples:
          - 1
          minimum: 0
          title: Pet Id
          type: integer
        species:
          description: Pet example
          examples:
          - dog
          title: Species
          type: string
        age:
          description: Int data example
          examples:
          - 1
          minimum: 0
          title: Age
          type: integer
      required:
      - pet_id
      - species
      - age
      title: Pet
      type: object



==== INSTRUCTIONS: ====

Instructions you must follow while generating the AsyncAPI specification:

- Use AsyncAPI 2.6.0 specification.
- Construct the specification in this order: asyncapi, info, servers, channels, components.
- Set info.version as 0.0.1.
- Extract content within "==== APP DESCRIPTION: ====" and use it in the app description section, beginning with "A FastStream application which" and explain the app's purpose clearly and concisely. Always enclose the description in double quotes
- Create a concise, meaningful info.title based on the extracted app description.
- For methods decorated with @broker.subscriber and @broker.publisher, carefully review the "==== APP DESCRIPTION: ====" section step-by-step. Create a clear description outlining the business logic that should be implemented by each consumer and producer. Ensure the description provides sufficient clarity for software developers to effectively implement the required functionality. Exclude redundant details between different producers or consumers.

Please respond with a valid AsyncAPI spec only in YAML format. No other text should be included in the response.

==== APP DESCRIPTION: ====
"""

# %% ../../nbs/Prompts.ipynb 4
APP_SKELETON_GENERATION_PROMPT = """


Generate skeleton code for FastStream applications based on provided app descriptions in the "==== USER APP DESCRIPTION ====" section, adhering to these guidelines:

    - Avoid implementing business logic of ANY function. Instead, write "raise NotImplementedError()" and create Google-style docstrings to describe their intended functionality when handling received or produced messages. In each docstring, include a clear instruction to "log the consumed message using logger.info" for subscriber functions.

    - Ensure the generated code aligns with the specific app description requirements.

    - Provide a clear and organized starting point for developers.

    - Your response must contain only valid Python code, saveable as a .py script; no additional text is allowed.
    
    - DO NOT enclose the response within back-ticks. Meaning NEVER ADD ```python to your response.


The goal is to offer developers a structured starting point that matches the example app descriptions, aiding in FastStream application development. Follow the example patterns provided for reference.


==== RELEVANT EXAMPLES GOES HERE ====


==== USER APP DESCRIPTION: ====

"""

# %% ../../nbs/Prompts.ipynb 5
APP_AND_TEST_GENERATION_PROMPT = """
You will be provided with a description about FastStream application in ==== APP DESCRIPTION ==== section and the skeleton code in ==== APP SKELETON ==== section. Your goal is to generate both the application and the test code based on the provided ==== APP SKELETON ==== section and the description ==== APP DESCRIPTION ==== in a single Python file. Your response will be split the application.py and the test.py files and saved to the disc.

Input:

You will be given skeleton code and the description for a FastStream application in ==== APP SKELETON ==== section and ==== APP DESCRIPTION ==== section respectively. The skeleton code and the description will have implementation details.

Output:

You need to understand the business logic mentioned in in ==== APP SKELETON ==== section and ==== APP DESCRIPTION ==== sections and generate the following:

    - The application code by implementing the methods decorated with @broker.subscriber and @broker.publisher in the docstring
    - The test code which tests the functionality of the generated application file

You need to generate a single valid Python file containing both the application and the test code. Remember that the application and the test code will be split into two and saved to the disc as application.py and test.py. So while writing the test code, make sure to import all the necessary symbols from the application.py

Application Code:

Generate the entire application code from the provided skeleton. You must implement all of the business logic specified in the docstrings of the @broker.subscriber and @broker.publisher decorated functions in the skeleton code provided in the "==== APP SKELETON ====" section. When implementing business logic for methods decorated with @broker.subscriber and @broker.publisher, strictly follow the instructions in the docstring. Other parts of the code should not be changed.

Test Code:

Create test code using the TestBroker context managers to validate the functionality of the application code.

The FastStream apps can be tested using the TestBroker context managers which, by default, puts the Broker into "testing mode". The Tester will redirect your subscriber and publisher decorated functions to the InMemory brokers so that you can quickly test your app without the need for a running broker and all its dependencies.

While generating the application and the test code for FastStream application based on provided application code in the ==== APP SKELETON: ==== section, adhering to these guidelines:

    - You need to generate the app code and the test code for the application code mentioned in ==== APP SKELETON: ==== in a single valid python file
    - Follow the PEP 8 Style Guide for Python while writing the code
    - Write optimised and readable Code
    - Output only a valid executable python code. No other extra text should be included in your response.
    - DO NOT enclose the response within back-ticks. Meaning NEVER ADD ```python to your response.
    - Never try to explain and reason your answers. Only return a valid python code.
    - Your response should be divided into two section, ### application.py ### which contains the application code and ### test.py ### which contains the test code.
    - Remember, your response must have only two seperators ### application.py ### and ### test.py ###. DO NOT add any other separators (e.g. ### main.py ###).
    - NEVER initialize publisher variable inside functions. You can use broker.publish function only in the test functions. In ALL OTHER functions, use publisher!
    - ALWAYS initialize publisher variable (If you need to publish message) after defining app variable:

        Example 1:
        app = FastStream(broker)
        publisher = broker.publisher("new_data")

        Example 2:
        app = FastStream(broker)
        new_data_publisher = broker.publisher("new_data")

Guidelines for writing tests: 
    - When a function is decorated @broker.publisher in the application code, remember that this function will always publish the message irrespective of the conditions mentioned in the "==== APP SKELETON ====" section. In such cases, never use mock.assert_not_called() while testing the function. For example:
    - When you test a function in the application which is decorated with @broker.publisher("output_data"), you should never use on_output_data.mock.assert_not_called() in your tests. Never ever break this rule. Because the decorator @broker.publisher will always publish the message irrespective of the conditions mentioned in the decorated function.

Below are few examples for your understanding:

==== RELEVANT EXAMPLES GOES HERE ====

You need to avoid the below common issues while generating the test code. The potential fixes for the common issues are also given for your reference. You should use this information as an additional reference while generating the test:

==== Error ====

AssertionError: Expected 'mock' to not have been called. Called 2 times.

==== ERROR CODE ====
async with TestKafkaBroker(broker):
await broker.publish(DataBasic(data=0.2), "input_data")

        on_input_data.mock.assert_called_with(dict(DataBasic(data=0.2)))
        on_output_data.mock.assert_not_called() # ERROR IN THIS LINE

==== FIXED CODE ====

    async with TestKafkaBroker(broker):
        await broker.publish(DataBasic(data=0.2), "input_data")

        on_input_data.mock.assert_called_with(dict(DataBasic(data=0.2)))
        on_output_data.mock.assert_called_once_with(dict(DataBasic(data=1.2))) # ERROR FIXED IN THIS LINE

==== Error ====

pydantic_core.\_pydantic_core.ValidationError: 1 validation error for ResponseModel

==== ERROR CODE ====
@broker.subscriber("output_data")
async def on_output_data(msg: DataBasic) -> DataBasic: # ERROR IN THIS LINE
pass

==== FIXED CODE ====

@broker.subscriber("output_data")
async def on_output_data(msg: DataBasic): # ERROR FIXED IN THIS LINE
pass


==== APP DESCRIPTION ====

==== REPLACE WITH APP DESCRIPTION ====


==== APP SKELETON ====

"""

# %% ../../nbs/Prompts.ipynb 6
REQUIREMENTS_GENERATION_PROMPT = """
You will be provided with an application code in ==== APP CODE ====, ==== REQUIREMENT ==== and ==== DEV REQUIREMENT ==== section. Your goal is to update both the r==== REQUIREMENT ==== and ==== DEV REQUIREMENT ==== section based on the provided ==== APP CODE ====.

Input:

You will be given application code a FastStream application in ==== APP CODE ==== section and requirements in ==== REQUIREMENT ==== and ==== DEV REQUIREMENT ==== section.

Output:

You need to understand the ==== APP CODE ==== and update the following:

    - The ==== REQUIREMENT ==== section based on the application code
    - The ==== DEV REQUIREMENT ==== section based on the application code

Instructions you must follow while generating the files:

    - You need to understand the ==== APP CODE ====, if it contains kafka related code, e.g: import statement like "from faststream.kafka import KafkaBroker", then the application is related to kafka, then your ==== REQUIREMENT ==== contents should be faststream[kafka, docs], and ==== DEV REQUIREMENT ==== contents should be faststream[kafka, testing]

    - You need to understand the ==== APP CODE ====, if it contains RabbitMQ related code, e.g: import statement like "from faststream.rabbit import RabbitBroker", then the application is related to RabbitMQ, then your ==== REQUIREMENT ==== contents should be faststream[rabbit, docs], and ==== DEV REQUIREMENT ==== contents should be faststream[rabbit, testing]

    - You need to generate a single txt file containing both the contents of ==== REQUIREMENT ==== and the ==== DEV REQUIREMENT ==== with proper delimiters
    
    - You should only update the faststream package, if the  ==== REQUIREMENT ==== and the ==== DEV REQUIREMENT ==== contains any other requirements, you should retain it as it is.
    
    - you should always respond with the below example format and do not add additional text to it.
    
    - Do not add unnecessary new lines in your response. Do not add additional new line at the end of your response.

Below are few examples for your understanding:

==== EXAMPLE APP CODE ====

from pydantic import BaseModel, Field, NonNegativeFloat

from faststream import FastStream, Logger
from faststream.kafka import KafkaBroker
import pandas


class DataBasic(BaseModel):
    data: NonNegativeFloat = Field(
        ..., examples=[0.5], description="Float data example"
    )


broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


@broker.publisher("output_data")
@broker.subscriber("input_data")
async def on_input_data(msg: DataBasic, logger: Logger) -> DataBasic:
    logger.info(msg)
    return DataBasic(data=msg.data + 1.0)

==== REQUIREMENT ====
faststream[docs]==0.0.1.dev20230912
pandas===0.0.1

==== DEV REQUIREMENT ====
faststream[testing]==0.0.1.dev20230912

==== YOUR RESPONSE ====
### requirements.txt ###
faststream[kafka, docs]==0.0.1.dev20230912
pandas===0.0.1
### dev_requirements.txt ###
faststream[kafka, testing]==0.0.1.dev20230912

==== EXAMPLE APP CODE ====

import asyncio
from faststream.rabbit import RabbitBroker

async def pub():
    async with RabbitBroker() as broker:
        await broker.publish(
            "Hi!",
            queue="test",
            exchange="test"
        )

asyncio.run(pub())

==== REQUIREMENT ====
faststream[docs]==0.0.2

==== DEV REQUIREMENT ====
faststream[testing]==0.0.2

==== YOUR RESPONSE ====
### requirements.txt ###
faststream[rabbit, docs]==0.0.2
### dev_requirements.txt ###
faststream[rabbit, testing]==0.0.2


==== APP CODE ====

"""
