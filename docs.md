#### NOTE : these infomations assume that you have compiled/frozen the program, if you haven't done so, you need to use `python gtar.py` instead
# Archiving
Use `gtar -as {file} -o {archive}` to archive one file/directory

Use `gtar -ao {archive} -S {files ... files}` to archive multiple files/directories

# Extracting
Use `gtar -es {archive}` to extract one archive

Use `gtar -eS {archives ... archives}` to extract multiple archive

# Detailed description
| Option | Usage |
| - | - |
| `-a --archive` | Archive mode |
| `-e --extract` | Extract mode |
| `-o [output file]` | Specify output file |
| `--out [output file]` |
| `-s [source file]` | Specify source file |
| `--source [source file]` |
| `-S [source files]` | Every following parameter is path to source files |
| `--sources [source files]` |
