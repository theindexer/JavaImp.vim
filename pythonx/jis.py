import vim
import re

def parseImports():
    # Compile the Regex to Match Import Statements.
    regex = re.compile("^\s*import\s\s*")

    # Find All Import Statements (normal and static).
    for line in vim.current.buffer:
        match = regex.match(line)
        if (match):
            # TODO: Do something with them.
            print line

parseImports()
