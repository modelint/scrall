"""
scrall_exceptions.py – Flatland specific exceptions
"""

# Every flatland error should have the same format
# with a standard prefix and postfix defined here
pre = "\nScrall parse error: ["
post = "]"


class ScrallException(Exception):
    pass

class ScrallParseError(ScrallException):
    def __init__(self, e):
        self.arp_error = e

    def __str__(self):
        return f"{pre}{self.arp_error}{post}"