"""pdf2yaml: Fast, structured PDF to YAML converter optimized for AI knowledge pipelines."""

from .pipeline import pdf_to_yaml
from .models import YamlDocument, Options

__version__ = "0.1.0"
__all__ = ["pdf_to_yaml", "YamlDocument", "Options"]
