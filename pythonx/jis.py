import vim
import re

topImports = vim.eval("g:JavaImpTopImports")
depth = int(vim.eval("g:JavaImpSortPkgSep"))
staticFirst = int(vim.eval("g:JavaImpStaticImportsFirst"))
importNormalList = []
importStaticList = []

# Find the Import Statements and parse them into some intermediate data structures.
def parseImports():
    # TODO: Would be better if these weren't globals.
    global importNormalList
    global importStaticList

    rangeStart = -1
    rangeEnd = -1

    importBegin = "^\s*import\s+" 

    # Compile the Regex to Match Normal Import Statements.
    regexNormal = re.compile(importBegin)

    # Compile the Regex to Match Static Import Statements.
    regexStatic = re.compile(importBegin + "static\s+")

    # Find All Import Statements (normal and static).
    lastMatch = -1
    for lineNum, line in enumerate(vim.current.buffer):
        match = regexNormal.match(line)
        if (match):
            # Indicate the Start of the Import Statement Range if not yet set.
            if rangeStart == -1:
                rangeStart = lineNum

            lastMatch = lineNum

            # Track Static and Normal Imports in different lists.
            match = regexStatic.match(line)
            if match:
                importStaticList.append(line)

            else:
                importNormalList.append(line)

    # Indicate the End of the Import Statement Range.
    rangeEnd = lastMatch

    return (rangeStart, rangeEnd)

# Sort the Import List.
def sort(pImportList):
    global topImports

    # Copy & Sort the whole list of imports first.
    importList = list(pImportList)
    importList.sort()

    # Interrim sorted list will live here.
    sortedImportList = list()

    # Iterate over each import pattern in topImports
    for importPattern in topImports:
        regex = re.compile("^\s*import\s+" + importPattern)

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

        # Last Match is the last import in the sequence the first match was
        # detected, but the imports never changed before the end of the import
        # list.
        if frstMatch != -1 and lastMatch == -1:
            lastMatch = len(importList) - 1

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

    return importList

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
def insertSpacing(importList, depth):
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

    return importList

def deleteRange(start, end):
    # Remove Existing Imports from the Buffer.
    del vim.current.buffer[start:end + 2]

# Update the Buffer with the current ordered list of Import Statements.
def updateBuffer(startLine, importList):
    # Edge Case.
    # Handle a situation where the range of imports is supposed to be at the
    # first line of the file.  The vim module doesn't seem to support this very
    # well...
    origLines = []
    if startLine == -1:
        # Copy the Original Lines in the Buffer.
        origLines = vim.current.buffer[:]

        # Delete the Original Lines (Leaving an empty Buffer).
        del vim.current.buffer[:]

        # Provide a non-negative number so that we insert below the first line.
        startLine = 0

    # Do not append an empty list since this will insert an additional newline.
    if len(importList):
        # Append the Sorted List to the Buffer.
        vim.current.buffer.append(importList, startLine)

        # Insert a newline at the end.
        vim.current.buffer.append("", startLine + len(importList))

    # If there were lines in the buffer originally which were deleted in the
    # Edge Case mentioned above,
    if origLines:
        # Append the original lines.
        vim.current.buffer.append(origLines)

        # Delete the First Line--which will always be blank.
        del vim.current.buffer[0]

    # Return Cursor Position After Inserted Lines.
    return startLine + len(importList)

# Extract Normal and Static Imports.
(rangeStart, rangeEnd) = parseImports()

# Sort Normal Imports.
importNormalList = sort(importNormalList)

# Sort Static Imports.
importStaticList = sort(importStaticList)

# Insert Spacing into Normal Import List.
importNormalList = insertSpacing(importNormalList, depth)

# Remove the range of imports.
deleteRange(rangeStart, rangeEnd)

## Update the Buffer with Static Imports first, then Normal Imports.
startLine = rangeStart - 1
if staticFirst:
    startLine = updateBuffer(startLine, importStaticList) + 1
    startLine = updateBuffer(startLine, importNormalList) + 1

else:
    startLine = updateBuffer(startLine, importNormalList) + 1
    startLine = updateBuffer(startLine, importStaticList) + 1
