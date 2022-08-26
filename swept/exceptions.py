class CantUncover(Exception):
    """When trying to uncover a cell that is in the wrong state."""


class CantToggleFlag(Exception):
    """When trying to toggle the flag of a cell that is not in the right state."""
