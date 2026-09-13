"""
NirmaanAI Phase 19: Text Cleaner & Credential Scrubber
Cleans ingested text, strips ANSI escape sequences, normalizes whitespace,
and scrubs credentials while preserving markdown headers and table formatting.
"""

import re
import unicodedata

# Regex for stripping ANSI escape sequences
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Regex for scrubbing credentials and connection URIs
CREDENTIAL_SCRUBBERS = [
    (re.compile(r"postgresql(?:\+psycopg)?://[^:]+:([^@]+)@", re.IGNORECASE), r"postgresql://***:***@"),
    (re.compile(r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE), r"\1='***'"),
    (re.compile(r"(password|secret|api_key|token)\s*:\s*['\"][^'\"]+['\"]", re.IGNORECASE), r"\1: '***'"),
]


class TextCleaner:
    """Provides safe, deterministic text normalization for factory knowledge chunks."""

    @staticmethod
    def clean(text: str) -> str:
        """
        Normalizes raw text into clean, safe chunk text.
        Preserves Markdown headings, bullet points, and tables.
        """
        if not text:
            return ""

        # 1. Strip ANSI escape sequences
        cleaned = ANSI_ESCAPE_RE.sub("", text)

        # 2. Scrub credentials / connection strings
        for pattern, replacement in CREDENTIAL_SCRUBBERS:
            cleaned = pattern.sub(replacement, cleaned)

        # 3. Normalize Unicode (NFKC)
        cleaned = unicodedata.normalize("NFKC", cleaned)

        # 4. Standardize line endings
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

        # 5. Remove excessive blank lines (more than 2 consecutive newlines)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        return cleaned.strip()

    @staticmethod
    def sanitize_heading(heading: str) -> str:
        """Normalizes section header text."""
        if not heading:
            return "General"
        # Remove leading hashes and whitespace
        h = re.sub(r"^#+\s*", "", heading).strip()
        # Remove markdown link formatting inside heading
        h = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", h)
        return h or "General"
