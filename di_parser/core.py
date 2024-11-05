import os
import xml.etree.ElementTree as ET
from io import TextIOBase
from typing import Optional, Union, IO
from dataclasses import dataclass
from pathlib import Path

# Exception for unsupported document type.
class UnsupportedDocumentType(Exception): ...

@dataclass
class DocumentItem:
    """
    The general data structure for document items.
    """
    sequence: str # The sequence number of the item.
    content: str # The text content of the item.
    sub_sequence: tuple["DocumentItem", ...] # A list of sub items.

    def __init__(self, sequence: str, content: str, sub_sequence: list["DocumentItem"]):
        # Automatically trim trailing whitespaces.
        self.sequence = sequence.strip() 
        self.content = content.strip()

        self.sub_sequence = tuple(sub_sequence)

    def __str__(self):

        seprator = "\n"

        if not self.content:
            # We assume these's no such case that content is empty but sequence number is there.
            full_content = ""
        else: # If there's content, add a space between the sequence number and the content.
            full_content = f"{self.sequence} {self.content}"

        # Recursively stringify the items in the subSequence.
        sub_content = "\n".join([str(item) for item in self.sub_sequence])

        if not full_content or not sub_content:
            # If either of them are empty, we don't need a new line.
            seprator = ""

        return full_content + seprator + sub_content
    
    @classmethod
    def from_node(cls, node: ET.Element) -> "DocumentItem":
        """
        Given a root node, return a document item object.
        """
        sequence_bullet: str = node.attrib.get("序號")
        content: str = ""
        sub_sequences: list["DocumentItem"] = []

        if not sequence_bullet:
            sequence_bullet = ""
            
        for child in node:
            if child.tag == "文字":
                if child.text:
                    content = child.text
                else:
                    content = ""
            elif child.tag == "條列":
                sub_sequences.append(cls.from_node(child)) # Recursively parse the sub sequences.
        
        ret = cls(sequence=sequence_bullet, content=content, sub_sequence=sub_sequences)
        return ret

# The "Description" and "Act" section can be treated as a DocumentItem.
@dataclass
class Section(DocumentItem):

    section_type: str # This attribute may be "說明" or "擬辦", indicating the type of the section.
    
    def __init__(self, section_type: str, content: str, sub_sequence: list["DocumentItem"]):
        super().__init__(section_type, content, sub_sequence)
        self.section_type = section_type

    def __str__(self):

        seprator = "\n"

        # Recursively stringify the items in the subSequence.
        sub_content = "\n".join([str(item) for item in self.sub_sequence])

        if not self.content or not sub_content:
            # If either of them are empty, we don't need a new line.
            seprator = ""

        return self.section_type + "：" + "\n" + self.content + seprator + sub_content
    
    @classmethod
    def from_node(cls, node: ET.Element) -> "Section":
        """
        Given a root node of section, return a Section object.
        """

        # Initial check.
        assert node.tag == "段落", "The node must be a paragraph."

        # Remove unnecessary colon, too ugly, who set an attribute like this?????????
        section_type: str = node.attrib.get("段名").replace("：", "")
        content: str = ""
        sub_sequences: list[DocumentItem] = []

        if not section_type:
            section_type = ""
            
        for child in node: # We follows the same logic as DocumentItem.
            if child.tag == "文字":
                if child.text:
                    content = child.text
                else:
                    content = ""

            elif child.tag == "條列":
                sub_sequences.append(DocumentItem.from_node(child)) # Recursively parse the sub sequences.
        
        ret = cls(section_type=section_type, content=content, sub_sequence=sub_sequences)
        return ret

@dataclass
class Document:
    document_type: str
    organization: str
    date: str # TODO: Implement a date object.
    subject: str
    description: Section
    act: Optional[Section]

    def __str__(self):
        return f"{self.document_type} | {self.organization} | {self.date}\n{self.subject}\n{str(self.description)}{"\n" + str(self.act) if self.act else ""}"
    
    @classmethod
    def from_node(cls, root_node: ET.Element) -> "Document":

        document_type = root_node.tag

        # Check if the document type is supported.
        if document_type not in ["函", "簽"]:
            raise UnsupportedDocumentType(f"Document type {document_type} is not supported.")

        # Parse organization.
        if document_type == "簽":
            organization = root_node.find("機關")[0].text
        elif document_type == "函":
            organization = root_node.find("發文機關")[0].text

        # Parse date.
        if document_type == "函":
            date = root_node.find("發文日期").find("年月日").text
        elif document_type == "簽":
            date = root_node.find("年月日").text

        subject = root_node.find("主旨").find("文字").text


        description = None # Placeholder
        act = None # Placeholder

        for sect in root_node.findall("段落"):
            if sect.attrib.get("段名") == "說明：":
                description = Section.from_node(sect)
            elif sect.attrib.get("段名") == "擬辦：":
                act = Section.from_node(sect)
        
        return cls(document_type=document_type, organization=organization, date=date, subject=subject, description=description, act=act)
    
def document_from_xml(string_or_pathlike: Union[str, Path, IO[str]]) -> Document:
    """
    Given a path or a string of the XML content, return a Document object.
    """
    if isinstance(string_or_pathlike, Path): # If the input is a path-like object.
        file_content = string_or_pathlike.read_text()
        root = ET.fromstring(file_content)
    
    # If the input is a string, it may be either a path or the content itself.
    elif isinstance(string_or_pathlike, str):
        if os.path.exists(string_or_pathlike): # If the string is a path.
            tree = ET.parse(string_or_pathlike)
            root = tree.getroot()
        else: # If the string is the XML content.
            root = ET.fromstring(string_or_pathlike)

    # If the input is a IO reader.
    elif isinstance(string_or_pathlike, TextIOBase):
        root = ET.fromstring(string_or_pathlike.read()) # Read the content and parse it.

    # Not supported
    else:
        print(type(string_or_pathlike))
        raise ValueError("The input must be either a string or a path-like object")
    
    return Document.from_node(root)

def remove_redundant_words(text: str) -> str:
    """
    ## 八股文 is bad, remove 咬文嚼字.
    """
    ng_list = ["請", "核示", "函", "為", "申請", "辦理", "鑒核", "簽", "。", "，", "檢陳", "申辦", "申辦", "「", "」"]

    for ng in ng_list:
        text = text.replace(ng, "")

    return text