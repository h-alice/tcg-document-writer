# DI File Parser
A parser for document object (*.di) files.

## Features
- Parse a document object file (*.di) and extract the necessary information.
- Provides a pretty-printed output of document content.

## Where to Find DI Files
Tipically, DI files are located inside `%LOCALAPPDATA%\KdApp\DOC_DIR` directory.

Inside individual document directories, you may find a file named `1.di`, that's what we need.

## API Documentation

### 1. `DocumentItem`

The `DocumentItem` class represents a general data structure for document items.

#### Fields

- **`sequence`**: `str`
  - The sequence bullet of the item, which is automatically trimmed of trailing or leading whitespaces.

- **`content`**: `str`
  - The text content of the item, also trimmed of trailing or leading whitespaces.

- **`sub_sequence`**: `tuple[DocumentItem, ...]`
  - A tuple containing sub-items of type `DocumentItem`. The tuple acted like an immutable list.

#### Methods

- **`__init__(self, sequence: str, content: str, sub_sequence: list[DocumentItem])`**
  - Initializes a `DocumentItem` with sequence, content, and a list of sub-sequences.

- **`__str__(self)`**
  - Returns a string representation of the `DocumentItem`, including its sequence, content, and recursively its sub-sequence items.

- **`from_node(cls, node: ET.Element) -> DocumentItem`**
  - Class method to create a `DocumentItem` from an XML node.

---

### 2. `Section`

The `Section` class extends `DocumentItem` and represents a section of a document, such as "Description" or "Act".

#### Fields

- **`section_type`**: `str`
  - Indicates the type of the section, such as "說明" (Description) or "擬辦" (Act).

#### Methods

- **`__init__(self, section_type: str, content: str, sub_sequence: list[DocumentItem])`**
  - Initializes a `Section` with a section type, content, and a list of sub-sequences.

- **`__str__(self)`**
  - Returns a string representation of the `Section`, including its type, content, and recursively its sub-sequence items.

- **`from_node(cls, node: ET.Element) -> Section`**
  - Class method to create a `Section` from an XML node.

---

### 3. `Document`

The `Document` class represents a complete document, including its metadata and content sections.

#### Fields

- **`document_type`**: `str`
  - The type of the document, such as "函" or "簽".

- **`organization`**: `str`
  - The organization associated with the document.

- **`date`**: `str`
  - The date of the document.

- **`subject`**: `str`
  - The subject of the document.

- **`description`**: `Section`
  - A `Section` object representing the description part of the document.

- **`act`**: `Optional[Section]`
  - An optional `Section` object representing the act part of the document if it exists.

#### Methods

- **`__str__(self)`**
  - Returns a string representation of the `Document`, including its type, organization, date, subject, description, and act.

- **`from_node(cls, root_node: ET.Element) -> Document`**
  - Class method to create a `Document` from an XML root node.

---

### Function

#### `document_from_xml(string_or_pathlike: Union[str, Path, IO[str]]) -> Document`

- Parses a string or path-like object containing XML content and returns a `Document` object.

## Notes for Current Version
Currently parser will ignores all additional attributes (such as serial number) in the document and preserves only the necessary information we may need.

We may implement parser for additional features in the future.

