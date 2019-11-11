import enum


class DuplicateObjectStrategy(enum.Enum):
    """Different strategies for dealing with a duplicate object already encountered in a table.

    RAISE: Raise an exception.

    IGNORE: Ignore the duplicate object regardless of its content, do not add it to the table or the object_name_map.

    REPLACE: Always use the duplicate object and replace the object in the object_name_map regardless of its content.

    REPLACE_IF_DIFFERENT: Use the duplicate object only if different then replace the object in the object_name_map

    REPLACE_LATER_COPY: Use the duplicate object only if the object copy number is greater than the original copy number
    then replace the object in the object_name_map (the original is retained in the list of objects).

    Other possibilities:

    - Walk through the attributes replacing any that have a greater copy number?
    """
    RAISE = enum.auto()
    IGNORE = enum.auto()
    REPLACE = enum.auto()
    REPLACE_IF_DIFFERENT = enum.auto()
    REPLACE_LATER_COPY = enum.auto()