import vim
import re

topImports = vim.eval("g:JavaImpTopImports")
depth = int(vim.eval("g:JavaImpSortPkgSep"))
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

# Determine if a separator is required between the two provided imports, given
# a depth into the imports to check.  Depth is the number of package levels to
# check (i.e. the number of dots in the import statement).
def isSeparatorRequired(prevImport, currImport, depth):
    prevList = prevImport.split(".", depth)
    currList = currImport.split(".", depth)

    del prevList[-1]
    del currList[-1]

    return prevList != currList

# Insert spacing into a sorted list of packages.
def insertSpacing():
    global importList
    global depth

    # Copy the importList into a separate variable so that we are not iterating
    # over the list we are editing.
    spacedList = list(importList)

    # Review each entry of the list, if a separator is required, insert it.
    row = 0
    prevImport = ""
    currImport = ""
    for currImport in importList:
        if not prevImport:
            prevImport = currImport

        if isSeparatorRequired(prevImport, currImport, depth):
            spacedList.insert(row, "")
            row += 1

        prevImport = currImport
        row += 1

    # Remove Last Blank Entry (if present)
    if not spacedList[-1]:
        del spacedList[-1]

    # Replace the import list with our spaced out copy.
    importList = spacedList

# Update the Buffer with the current ordered list of Import Statements.
def updateBuffer():
    global importList

    # Remove Existing Imports from the Buffer.
    del vim.current.buffer[rangeStart:rangeEnd + 2]

    importStartLine = rangeStart - 1

    # Append the Sorted List to the Buffer.
    vim.current.buffer.append(importList, importStartLine)

    # Insert a newline at the end.
    vim.current.buffer.append("", importStartLine + len(importList))


# TODO: Would be better if this were in a separate file (with this file being a library object).
parseImports()
sort()
insertSpacing()
updateBuffer()
