"""Audio to text tools.

This module provides tools that can be called by language models.
"""

from programs.Audio2Text.functions import process_audio, merge_speakers, merge_speakers_engine

__all__ = [
    "process_audio",
    "merge_speakers",
    "merge_speakers_engine",
]
