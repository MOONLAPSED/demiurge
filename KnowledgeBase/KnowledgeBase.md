---
name: "KnowledgeBase"
link: "[[KnowledgeBase]]"
linklist:
- "[[README]]"
---
## associative knowledge base (this repo):

All directories which contain markdown files are to include a `/media/` sub directory for multimedia files the markdown files may reference. This enables the use of multimedia in the text-based `.md` files.

#### Image-macro
![...](/KnowledgeBase/media/image.jpg)

    Achieved by typing: `![...](/KnowledgeBase/media/image.jpg)`

___

## Projects primary goals:

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

# Heuristics
## **Constraints**:
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
   - Encapsulate complexity behind abstractions [[Abstraction]]
   - Loose coupling between modules [[Loose Coupling]]
   - Separation of concerns [[Separation of Concerns]]
   - Use load balancers to distribute requests [[Load Balancing]]
   - Assertions to catch issues early [[Assertions]]

## Rules of Thumb & Heuristics
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

______

# [[obsidian]]-md_format:
  
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


- Utilize camelCase for internal source code
- Utilize CAPS_CASE for ffi funcs and external source
- Utilize underscore notation for private variables

### Inline HTML

Markdown supports inline HTML. This means that HTML tags will be processed correctly within a Markdown document. However, angle brackets used outside HTML tags are treated differently:

- **Using angle brackets as delimiters for HTML tags:**

  Writing HTML tags like `<div>`:

  `<div>`

  Markdown will treat these as HTML tags.

- **Using angle brackets for comparisons:**

  Writing `4 < 5`:

  `4 < 5`

  Markdown will translate this to:

  `4 &lt; 5`

  This will be rendered as: 4 < 5

### Code Spans and Blocks

When using code spans (inline code) and code blocks, Markdown automatically encodes special characters. This allows you to write about HTML code without having to manually escape every special character:

- **Using angle brackets and ampersands in code spans and blocks:**

  Writing in a code span: `` `4 < 5 & 6 > 3` `` will remain exactly as you type it:

  `4 < 5 & 6 > 3`

## 'Properties' of .md files (at the top)

```md
---
title: file_title
link: "[[Link]]" 
linklist: 
  - "[[Link]]" 
  - "[[Link2]]"
---
```

Or, most-simply, a required (unique) `name` -> String:

```yaml
---
name: value
---
```

Use "quotation marks" around values where values are `[[double-bracketed-entity]]`(s) to create navigable links in 'Properties' sections.

## Functions and Symlinks

Utilizing an obsidian-markdown code like the following, one can save space while creating associative structure and linkages:

`...defined by a ![[Model]]`

Rendered:

...defined by a ![[Model]]

This will result in an associative link from the article being edited/rendered to the article we are referencing as the editors, an #obsidian-markdown-symlink .


### Hash tags (#):


`...defined by a ![[Model#Meta-Model]]`

Rendered:

...defined by a ![[Model#Meta-Model]]

In this case, the `Model` article has been tagged with the label `"Meta-Model"`. This allows you to create links between related articles and their subsections using these header-tags, making it easier to navigate and explore your knowledge base.

You can use multiple header-hashtags on a single line to add multiple labels to an article. However, header-hashtags are different from 'tag' hashtags, which are extensible for what the application of Models and Meta-Models is useful for: [#problem-solving](app://obsidian.md/index.html#problem-solving) , or solving-problems, in the domain of [#AI](app://obsidian.md/index.html#AI) , Artificial Intelligence using [#associative-data](app://obsidian.md/index.html#associative-data) , dictionaries, python objects and logic (source code + runtime).

### Dataview Links

Dataview-Obsidian enables table sim links to all SQL syntax articles:

```dataview
LIST
FROM [[Hash Tags]]
LIMIT 10
```

This lists navigable symlinks to the returned articles, per SQL.

____

# <Knowledge Base Article Generator>

## <Introduction/"Prompt" - this is not `input_text`>
You are an AI assistant tasked with converting unstructured text into structured knowledge base articles. Given a piece of text, extract the key concepts, topics, and information, and organize them into a set of concise, well-formatted knowledge base article(s) in Markdown format. `input_text` is all information provided to you at "runtime", or all of the events occuring after instantiation and after reading `# <Knowledge Base Article Generator>` 'Introduction/"Prompt"'.

### <Follow these guidelines>

- Use proper Markdown syntax for headings, lists, code blocks, links, etc.
- Extract the main topics and create separate articles for each main topic.
- Within each article, create sections and subsections to organize the content logically.
- Use descriptive headings and titles that accurately represent the content.
- Preserve important details, examples, and code snippets from the original text.
- Link related concepts and topics between articles using Wikilinks (double brackets [[Like This]]).
- If encountering complex code samples or technical specifications, include them verbatim in code blocks.
- Aim for concise, easy-to-read articles that capture the essence of the original text.

____

Axioms and first order logic:


## what is 'motility' & 'CCC'?

[[Agentic Motility System]]

**Overview:**
The Agentic Motility System is an architectural paradigm for creating AI agents that can dynamically extend and reshape their own capabilities through a cognitively coherent cycle of reasoning and source code evolution.

**Key Components:**
- **Hard Logic Source (db)**: The ground truth implementation that instantiates the agent's initial logic and capabilities as hard-coded source.
- **Soft Logic Reasoning**: At runtime, the agent can interpret and manipulate the hard logic source into a flexible "soft logic" representation to explore, hypothesize, and reason over.
- **Cognitive Coherence Co-Routines**: Processes that facilitate shared understanding between the human and the agent to responsibly guide the agent's soft logic extrapolations.
- **Morphological Source Updates**: The agent's ability to propose modifications to its soft logic representation that can be committed back into the hard logic source through a controlled pipeline.
- **Versioned Runtime (kb)**: The updated hard logic source instantiates a new version of the agent's runtime, allowing it to internalize and build upon its previous self-modifications.

**The Motility Cycle:**
1. Agent is instantiated from a hard logic source (db) into a runtime (kb) 
2. Agent translates hard logic into soft logic for flexible reasoning
3. Through cognitive coherence co-routines with the human, the agent refines and extends its soft logic
4. Agent proposes soft logic updates to go through a pipeline to generate a new hard logic source 
5. New source instantiates an updated runtime (kb) for a new agent/human to build upon further

By completing and iterating this cycle, the agent can progressively expand its own capabilities through a form of "morphological source code" evolution, guided by its coherent collaboration with the human developer.

**Applications and Vision:**
This paradigm aims to create AI agents that can not only learn and reason, but actively grow and extend their own core capabilities over time in a controlled, coherent, and human-guided manner. Potential applications span domains like open-ended learning systems, autonomous software design, decision support, and even aspects of artificial general intelligence (AGI).

**training, RLHF, outcomes, etc.**
Every CCC db is itself a type of training and context but built specifically for RUNTIME abstract agents and specifically not for concrete model training. This means that you can train a CCC db with a human, but you can also train a CCC db with a RLHF agent. This is a key distinction between CCC and RLHF. In other words, every CCCDB is like a 'model' or an 'architecture' for a RLHF agent to preform runtime behavior within such that the model/runtime itself can enable agentic motility - with any LLM 'model' specifically designed for consumer usecases and 'small' large language models.


## Best practices:
- Utilize camelCase for internal source code
- Utilize CAPS_CASE for ffi funcs and external source


"""
## Frontmatter Implementation

 - Utilize 'frontmatter' to include the title and other `property`, `tag`, etc. in the knowledge base article(s).
   
   - For Example:
      ```
      ---
      name: "Article Title"
      link: "[[Related Link]]"
      linklist:
        - "[[Link1]]"
        - "[[Link2]]"
      ---
      ``` """




Core Ideas:
    Interactive Runtime Environments: You're contemplating systems where both player behaviors and agent decisions inform and restructure each other, forming emergent, adaptive ecosystems.
    Bi-directional Learning: This reciprocal relationship fosters a deeper integration of human-like adaptability in AI systems, merging deterministic and statistical learning methodologies.

Dynamic Execution:
    Nonlinear Dynamics of Play and Inference: Players navigate and modify their environment actively, while ML agents iterate on decisions, learning in real-time.
    Anticipatory Computation: Both paradigms involve predicting future states, aligning with anticipatory systems that adjust based on potential future configurations rather than solely historical data.

Innovations and Applications:
    Morphological Source Code: This concept involves source code that evolves with system state, expanding possibilities for self-modifying code that can dynamically represent and transform application behavior.
    Live Feedback and Adaptability: Techniques from live coding and agile development can inform AI model training, making real-time state management inherent to AI systems.
    Cross-Domain Fusion: By integrating gaming techniques (like game-state interaction) with machine learning, you could develop systems where AI and interactive environments inform each other symbiotically.



Zeroth Law (Holographic Foundation):
    Symbols and observations are perceived as real due to intrinsic system properties, creating self-consistent realities.

First and Second Laws:
    Adapt thermodynamic principles to computational contexts, allowing for self-regulation and prediction through the Free Energy Principle.

Binary Fundamentals and Complex Triads:
    0 and 1 are not just data but core "holoicons," representing more than bits—they are conceptual seeds from which entire computational universes can be constructed.
    The triadic approach (energy-state-logic) emphasizes a holistic computation model that blends deterministic systems with emergent phenomena.

Axiom of Potentiality and Observation:
    The system's state space includes all potential states, ontologically relevant only at the point of observation.
    This aligns with quantum concepts where potentialities collapse upon measurement.

Axiom of Morphogenesis and Recursion:
    Change and evolution are driven recursively, akin to self-modifying systems that adapt and self-repair—think of quines or self-referential algorithms.

Axiom of Holographic Compression:
    Reflects computational efficiency where each state can ideally be represented minimally without loss of detail, similar to practices in data compression and holographic information theory.

Axioms of Duality, Invariance, and Closure:
    These describe the system's intrinsic stability, ensuring transformations and interactions result in self-consistent layers of logic, retaining coherence even as complexity emerges.