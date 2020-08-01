import os
import typing


def common_directory_prefix(files: typing.Sequence[str]) -> str:
    """Returns the common directory prefix from a list of file paths"""
    prefix = os.path.commonpath(files)
    prefix = prefix[:1 + prefix.rfind(os.sep)]
    return prefix


def common_directory_prefix_len(files: typing.Sequence[str]) -> int:
    """Returns the length of the common directory prefix from a list of file paths"""
    return len(common_directory_prefix(files))
