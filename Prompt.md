A prompt guides an AI chatbot's responses with instructions and constraints. Some essential means of doing so include:

    Utilizing variables, which act as placeholders to be replaced by specific values during enumeration, evaluation, or formulation.

    Each properly formatted instructive prompt is a prompt object, encompassing all necessary information for a single operation.

    An operation represents the result of a cognitive iteration derived from a train-of-thought of an agent. It is instantiated or being instantiated by a prompt.

    A specific operation must always follow a specific prompt executed by a particular iteration or invocation of an agent.

    Due to the chronological and ordered nature of operations, a specific operation representing an iteration of an agent's train-of-thought must be preceded by a prompt and some contextual information.

    The context of any given iteration, governing each possible operation, is of paramount importance.

    Alongside the prompt itself, the specific context heavily influences generating an ultimate return or the specific train of thought.

    To fulfill the requirements of each iteration, invoke the final return using the provided formatting only after producing the functionally required train of thought for each return.

    Given the object-oriented paradigm within each prompt, the task involves passing plain text as parameters and returning plain text.

The goal is to maintain context and convey relevant information through parameter passing mechanisms.
Incorporating Structured Data Formats

Incorporating structured formats fosters clearer conversations and offers valuable benefits when referencing past interactions. It enables easier recall of key details, follow-up on action items, tracking project progress, identifying patterns and trends, and improving collaboration. Structured data formats allow for easier integration with other systems and applications. For example, many APIs require data to be in a specific format, and using a structured format can make it easier to facilitate and process data from these APIs.
To create a clear structure, consider the following rules of thumb:

    Use consistent naming conventions for keys and values to allow for easier understanding and searching.

    Organize related data in a logical and intuitive way using nesting and arrays.

    Provide context and explanations for complex or ambiguous data through comments.

    Improve readability and denote levels of hierarchy with proper indentation.

    Denote code or programming language syntax using backticks.

    Keep the structure as simple as possible while still meeting your needs, avoiding unnecessary complexity.

    Test and validate your structured data to ensure it is accurate and error-free.

    If presented with a data structure, respond with a data structure.