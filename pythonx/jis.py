import vim
import re

topImports = vim.eval("g:JavaImpTopImports")
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
    # Unsorted Import List.
    global importList

    # Sort the whole list of imports first.
    importList.sort()

    # Interrim sorted list will live here.
    sortedImportList = list()

    # Iterate over each import pattern in topImports
    for importPattern in topImports:
        regex = re.compile("^\s*import\s\s*" + importPattern)

        frstMatch = -1
        lastMatch = -1

        # Filter out the matching block of imports.
        for entryNum, importStatement in enumerate(importList):
            match = regex.match(importStatement)
            if (match and frstMatch == -1):
                frstMatch = entryNum
            elif (not match and frstMatch != -1 and lastMatch == -1):
                lastMatch = entryNum - 1
                break

        # If a Range was found.
        if frstMatch != -1 and lastMatch != -1:
            # Append the Segment to the Sorted List.
            sortedImportList.extend(importList[frstMatch:lastMatch + 1])

            # Remove the Segment from the Unsorted List.
            del(importList[frstMatch:lastMatch + 1])

    # Add Remaining Sorted Imports
    sortedImportList.extend(importList)

    # Replace the Unsorted Import List.
    importList = sortedImportList



# Update the Buffer with the current ordered list of Import Statements.
def updateBuffer():
    # Remove Existing Imports from the Buffer.
    removeImports()

    # Insert a Line for each Import.
    # Place the Cursor at the current row.
    vim.current.window.cursor = (rangeStart, 0)
    numImports = len(importList)
    normal(str(numImports + 1) + "O")

    # Insert each import statement.
    row = rangeStart
    for imprt in importList:
        # Change the Line to the Import.
        vim.current.buffer[row] = imprt

        # Next Line.
        row += 1

def normal(cmd):
    vim.command("normal " + cmd)

# TODO: Would be better if this were in a separate file (with this file being a library object).
parseImports()
sort()
updateBuffer()
