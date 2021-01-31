# Database Architecture

### Database Architecture

![image-20210131201632831](https://i.loli.net/2021/01/31/pDedWLKnj43bhQf.png)

Database data is stored in files in disk and files are read and written in blocks to improve performance and simplify transaction processing.

-   Buffer Manager: caches disk pages that mostly queried in memory to ensure that disk is only accessed when necessary;
-   File Manager: exposes raw file data to the DB, allows blocks or pages to be read from a file, allows files to be created or deleted as well;
-   Transaction Manager: works closely with the *buffer manager*, in charge of recording every modification of the DB, ensures pages are written back to disk in a way that also satisfies transaction properties.

All three managers collectively comprise the *storage manager*.

