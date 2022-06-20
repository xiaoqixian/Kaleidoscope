# Rust I/O

### Accepting Command Line Arguments

To read the values of command line arguments we pass in, we need a function provided in Rust's standard library, which is `std::env::args`. This function returns an iterator of the command line arguments, and we can call the `collect` method on an iterator to turn it into a collection. 

Note that `std::env::args` will panic if any argument contains invalid Unicode. If you program needs to accept arguments containing invalid Unicode, use `std::env::args_os` instead. That function returns an iterator that produces `OsString` values instead of `String` values. 

### Reading a File

Rust provides the `std::fs` module for file processing.

The module has such methods:

-   `read`: read the entire contents of a file into a bytes vector.
-   `read_to_string`: read the entire contents of a file into a string.
-   `read_link`: read a symbolic link, return the file that the link points to.
-   `write`: Write a slice as the entire contents of a file.

