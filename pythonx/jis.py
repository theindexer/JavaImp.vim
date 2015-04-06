import vim
import re

importList = []
rangeStart = -1
rangeEnd = -1

# Find the Import Statements and parse them into some intermediate data structures.
def parseImports():
    # TODO: Would be better if these weren't globals.
    global rangeStart
    global rangeEnd
    global importList

    # Compile the Regex to Match Import Statements.
    regex = re.compile("^\s*import\s\s*")

    # Find All Import Statements (normal and static).
    lastMatch = -1
    for lineNum, line in enumerate(vim.current.buffer):
        match = regex.match(line)
        if (match):
            # Indicate the Start of the Import Statement Range if not yet set.
            if rangeStart == -1:
                rangeStart = lineNum

            lastMatch = lineNum

            # Add this line to the list of import lines.
            importList.append(line)

    # Indicate the End of the Import Statement Range.
    rangeEnd = lastMatch

# Remove the Imports from the Buffer.
# parseImports must be called first.
def removeImports():
    del vim.current.buffer[rangeStart:rangeEnd + 2]

# Sort the Import List.
def sort():
    importList.sort()

# Update the Buffer with the current ordered list of Import Statements.
def updateBuffer():
    removeImports()
    # TODO: Buffer is not actually updated just yet.
    for imprt in importList:
        print imprt


# TODO: Would be better if this were in a separate file (with this file being a library object).
parseImports()
sort()
updateBuffer()
