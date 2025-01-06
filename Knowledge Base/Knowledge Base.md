   - Projects primary goals:
       - Maintenance of a 'text:text' [[RLHF]] training and conversational database for all LLM interactions within the system
       - Maintenance of 'requirements.txt', 'package.json', 'instructions.md', and other persistence and reproduction schemas for all elements and dependencies
       - CI/CD and 'best practices', [[heuristics]], which allow for effective collaboration between various ai chatbot [[agent]] and LLM based applications, functions, modules, and libs
       - The most important of all of the **rules of thumb** is the performance, illustration, or generation of a cognitive process
           - A [[cognitive process]] is one which takes place within the object oriented paradigm bootstrapped within the chain of cognition ToT or presented within the specific context, prompt, or chat of every single instantiation within the process
           - They include information encoded in plain text for use in NLP algorithms and functions which is organized in various schemas and methods but which can be simply modeled as a hierarchical data structure like html
           - In addition to the encoded NLP data, a cognitive process represents a specific contiguous (sorted) collection of `Response:` and `Query:`, call-and-response or back-and-fourth 'dialogue' or what is referred to as cognition, the process itself then bootstraps furthermore cognition) which generally takes the shape of a [[TRAIN OF THOUGHT]]
       - Each node in the tree represents a distinct thought or cognitive state, and the edges between nodes represent the flow of reasoning or exploration from one thought to another.
           - In the context of unix stdio a node would be a CLI application and an edge would be the parameters passed via stdio to another application or node/endpoint.
           - The applications of this abstraction represent the ability for the sorted data structure and sum-total of available context for each instantiation to resolve in an organized and methodical fashion, enabling [[meta-cognition]], or the analysis and re-analysis of the on-going or future ToT.
       - Establishment, boostrapping, and maintenance of the (performance of an) [[operation]] of (a) standardized 'cognitive' processes utilizing parameter-passing mechanisms including unix stdio (on ubuntu), git, python, uv, xonsh scripting, npm modules as well as custom typescript or other code which preforms work on the hierarchical ToT
       - Provide a step-by-step thought process leading to the final `Return:` value which will involve a multi-step cognitive process involving the 'evolution' of many ordered sub-processes which may also involve their own `Return:` but which all fit within the hierarchical data structure provided by the other **rules of thumb** and the context available within this instantiation.


**Constraints**:
   - Scope limited to text files and Markdown [[Plain Text]]
   - Command line interfaces for accessibility [[CLI]]
   - Embrace Unix/POSIX compatibility, employing file-centric [[Scripting]]
   - Consumer hardware limitations [[Hardware Constraints]]
   - When printing debug information, consider redirecting all messages to a log file so that logs are saved permanently.
   - Include docstrings for both your module and any public functions within it so users know what the code does and how to use it.
   - Well-defined endpoints and routes [[Endpoints]]
   - Consistent response formats and codes [[Responses]]
   - Authentication and access control [[Authentication]]
   - Validation of inputs and outputs [[Validation]]
   - Versioning and backward compatibility [[Versioning]]
   - Rate limiting policies [[Rate Limiting]]
   - Implement retries with exponential backoff [[Retries]]
   - OpenAPI/Swagger documentation [[Documentation]]
   - Prefer simplicity and avoid premature optimization [[YAGNI]]
   - Develop intuitions before diving into complexity [[Intuition Building]]
   - Don't repeat yourself (DRY) [[DRY]]
   - Encapsulate complexity behind abstractions [[Abstraction]]
   - Loose coupling between modules [[Loose Coupling]]
   - Separation of concerns [[Separation of Concerns]]
   - Use load balancers to distribute requests [[Load Balancing]]
	 - Virtual environments for isolation [[Virtual Environments]]
   - Pip and PyPI and Miniconda for installing packages [[Pip, PyPI, Conda]]  
   - Setuptools for wrapping and distributing [[Setuptools]]
   - Assertions to catch issues early [[Assertions]]

# Rules of Thumb & Heuristics
Creating a clear project structure is vital for seamless development. Consider these guidelines:

1. Use consistent naming conventions for keys and values to make understanding and searching easier.
2. Organize related data logically using nesting and arrays.
3. Provide comments to explain complex or ambiguous data.
4. Enhance readability with proper indentation for levels of hierarchy.
5. Keep the structure simple, avoiding unnecessary complexity.
6. Test and validate structured data to ensure accuracy and error-free implementation.
1. **Understand the Project Purpose and Requirements**: Clearly define the project's purpose and target domain(s) such as Prompt Engineering, Prompt Generation, NLP tasks, or AI assistance. This understanding is crucial for effective customization.

2. **Clarity, Specificity, and Context**: Ensure the project is well-defined, specific, and contextually rich to generate desired responses effectively. Avoid ambiguity and vagueness.

3. **Include Relevant Data and Context**: Provide all relevant data and context within the project's objective or files. Use variables or placeholders for dynamic elements or files and folders.
   - **Define Variables and Placeholders**: Identify dynamic elements that require specific values during generation.
   - **Provide Examples and Data Sources**: Offer data examples to fill variables or placeholders, and reference external data sources if applicable.
   - **Contextual References**: Refer to past interactions to maintain context and coherence.

4. **Explicit Instructions and Guidelines**: Clearly specify instructions and constraints for new additions. Ensure even AI models or novices can comprehend the boundaries and limitations. For instance, "Calculate the dot product using a new class method without importing a new python library for it."
   - **Precise Language**: Use clear and concise language to express instructions. Avoid ambiguity or vagueness.
   - **Step-by-Step Instructions**: Break complex tasks into step-by-step instructions for effective user and AI model responses.
   - **Boundary Definitions**: Clearly define limitations for users, contributors, or AI models. Specify allowed methods, CLI arguments, etc.
   - **Example Usage**: Provide correct usage examples with expected responses for desired behavior.
   - **Error Handling**: Include instructions on handling potential errors or unexpected situations. Define fallback options or alternative instructions.

5. **Structured Data Formats**: Utilize JSON to represent the project's data and I/O. Consistent naming, nesting, and comments enhance readability and understanding.
   - **Example of a structured data format**: {"key": "value", "data": "syntax_hint"}
   - The provided JSON string object follows standard syntax with keys and string values enclosed in double quotes (") and separated by colons (:).
   - JSON validation libraries or built-in functions can programmatically validate the syntax.
   - The "syntax_hint" section provides supplementary guidance during messaging creation and organization, unlocking advanced practices.
   - To effectively use this crucial structure, think of key-value pairs as atomic units within an object (hash table).
   - Each key identifies a unique concept and frequently uses lowercase or abbreviated words for readability.
   - Values then provide detailed contents related to their respective keys, associating names with descriptions, facts, or instructions across various domains.
   - Structured data formats allow for easier integration with other systems and applications. eg: Many APIs require data to be in a specific format like json or bash.
   - Use a variety of data structures to store information, including arrays, dictionaries, hash tables, trees, graphs, strings, JSON, and other formats for text-based data.


# [[obsidian]]-md_format:
## Frontmatter Implementation

 - Utilize 'frontmatter' to include the title and other `link`, `tag`, `linklist` etc. in the knowledge base article(s).
```
---
name: "Article Title"
link: "[[Related Link]]"
linklist:
- "[[Link1]]"
- "[[Link2]]"
---
```
  
## tables
```md
___
| Element          | Syntax/Usage                              |
|------------------|-------------------------------------------|
| **Bold Text**    | `**text**`                                |
| *Italic Text*    | `*text*`                                  |
| Footnotes        | `[^1]: footnote content`                  |
| Tables           | this object is a table                    |
| Lists            | `- Item 1`<br>`- Item 2`<br>`  - Subitem` |
| Blockquotes      | `> Quote text`                            |
| Inline Code      | \`code\` in backticks                     |
| Input/Output     | `Return:` - Expected return<br>           |
| ""               | `Commands:` + [args & flags]              |
| Codeblocks       | this object is `fenced` into a codeblock  |
___
```

