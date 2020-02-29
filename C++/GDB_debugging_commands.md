#### **GDB debugging commands**

1. commonly used commands

| Command                            | explanation                                                  |
| ---------------------------------- | ------------------------------------------------------------ |
| gdb program                        | start gdb, program is your program's name                    |
| gdb program core                   | start gdb, debug your program and your core file <br>simultaneously. But you have to set your system <br>to produce core file. |
| file <file_name>                   | load the executable file that to be debugged                 |
| r                                  | shorthand for run, run the debugged file.<br> If no breakpoints are set, then run the whole file, <br>else stop at the first breakpoint. |
| c                                  | shorthand for continue, continue to the next breakpoint.     |
| b line_number <br>b func name <br> | b for breakpoint. b + line number means add a <br>breakpoint at that line. Also, b + function name <br>means add a breakpoint at the entry of the function. |
| d [serial number]                  | delete breakpoint                                            |
| s n                                | s: run a row of source code. If a function was <br>   called, then entry the function. <br>n: run a row of source code. If a function was <br>   called, the function would be executed as well.<br>This two commands can only be used when you compile<br>the code with a "-g" option. |
| i                                  | display all kinds of information                             |
| q                                  | exit the gdb environment                                     |

2. check all breakpoints

   ```info b```

3. clear breakpoints

   ```clear```:clear all breakpoints

   ```clear function```:clear breakpoints set on functions

   ```clear linenum```:clear breakpoints set on the specific line

   ```clear filename:linenum```:clear breakpoints set on the specific line in the specific file

   ```disable [breakpoints] [range]```:disable breakpoints, [breakpoints] refers to specific breakpoints number. If not specified, disable all the breakpoints.

   enable [breakpoints] [range]:enable breakpoints, two arguments refers the same as the previous one.

4. view runtime data

   ```print```:print variable value, string or expression

   ```p var```:print the value of var

   ```p expression```:run the expression and print the result. But GDB can't use the macro in the code.


#### more detailed information in here:https://blog.csdn.net/Linux7985/article/details/52399439?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task

   