"""Pydantic data models for structured PDF-to-YAML conversion."""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Options(BaseModel):
    """Conversion options for pdf2yaml."""
    ocr_mode: str = "auto"          # "off", "auto", "tesseract"
    ocr_lang: str = "eng"
    export_images: bool = False
    detect_tables: bool = True
    detect_math: bool = True
    include_metadata: bool = True
    preview_only: bool = False


class EquationNode(BaseModel):
    """Representation of a mathematical equation."""
    id: Optional[str] = None
    latex: str
    description: Optional[str] = None


class TableNode(BaseModel):
    """Representation of a structured table."""
    id: Optional[str] = None
    caption: Optional[str] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)


class SectionNode(BaseModel):
    """Representation of a logical section or heading block."""
    title: str
    level: int = 1
    paragraphs: List[str] = Field(default_factory=list)
    equations: List[EquationNode] = Field(default_factory=list)
    tables: List[TableNode] = Field(default_factory=list)


class PageNode(BaseModel):
    """Representation of a single page in the PDF."""
    page_number: int
    sections: List[SectionNode] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    """Document metadata."""
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    total_pages: int = 0
    source_file: Optional[str] = None


class YamlDocument(BaseModel):
    """Root model representing the entire converted document."""
    metadata: DocumentMetadata
    pages: List[PageNode] = Field(default_factory=list)
