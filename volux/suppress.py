"""Define a context manager to suppress stdout and stderr."""

import os
from typing import Any

# full credit for this code goes to this post by jeremiahbuddha on stackoverflow:
# https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions


class SuppressStdoutStderr(object):
    """A context manager for doing a "deep suppression" of stdout and stderr in Python.

    i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).
    """

    def __init__(self) -> None:
        """Instatiate suppresser class. Should always be instansiated through the use of python's 'with'."""
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self) -> None:
        """Assign the null pointers to stdout and stderr."""
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_: Any) -> None:
        """Re-assign the real stdout/stderr back to (1) and (2)."""
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)
