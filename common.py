from di_parser import Document

def stringify_md(doc: Document) -> str:
    """
    Stringify a Document object in Markdown style.
    """
    return_str = ""
    return_str += f"# {doc.document_type}\n"
    return_str += f"## 主旨\n"
    return_str += f"{doc.subject}\n"
    return_str += f"## 說明\n"
    return_str += f"{doc.description.stringify('-', ignore_section_type=True)}\n"

    if doc.act:
        return_str += f"## 擬辦\n"
        return_str += f"{doc.act.stringify(ignore_section_type=True)}\n"

    if doc.receiver:
        return_str += f"## 收文者\n"
        for recv in doc.receiver:
            if recv.title:
                return_str += f"- {recv.receiver_type}: {recv.title}\n"

    return return_str