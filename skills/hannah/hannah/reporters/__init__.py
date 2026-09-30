"""Race Control comms — output formatters."""

from .console import ConsoleReporter
from .json import JSONReporter

__all__ = ["ConsoleReporter", "JSONReporter"]
