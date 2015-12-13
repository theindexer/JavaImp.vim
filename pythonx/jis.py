import vim
import re

# TODO: Move all of this into a class.

importBegin = "^\s*import\s+" 
topImports = vim.eval("g:JavaImpTopImports")
depth = int(vim.eval("g:JavaImpSortPkgSep"))
staticFirst = int(vim.eval("g:JavaImpStaticImportsFirst"))
importTopImpList = []
importMiddleList = []
importStaticList = []

# Extract and Separate Imports.
def parseImports():
    separateImports(extractImports())

def sortImports():
    global importTopImpList
    global importMiddleList
    global importStaticList

    fullySortedImportStatements = list()

    # Sort Top Imports
    regexTopImports = topImports
    importTopImpList = regexSort(importTopImpList, regexTopImports)

    # Sort Middle Imports.
    importMiddleList = regexSort(importMiddleList, list())

    # Sort Static Imports.
    importStaticList = regexSort(importStaticList, list())

    # Add Static Imports first (if configured to do so)
    if staticFirst:
        fullySortedImportStatements.extend(importStaticList)

    # Add Top Imports
    fullySortedImportStatements.extend(importTopImpList)

    # Add Middle Imports
    fullySortedImportStatements.extend(importMiddleList)

    # Add Static Imports last (if configured to do so)
    if not staticFirst:
        fullySortedImportStatements.extend(importStaticList)

    return fullySortedImportStatements

# Sort the provided importStatements first by the provided importRegexList, then
# alphanumerically.
def regexSort(importStatements, importRegexList):
    global importBegin

    regexSortedList = list()

    # First sort the list alphanumerically.
    importStatements.sort()

    # If the regex list is non-empty
    if len(importRegexList) > 0:
        # Precompile the regexes from the provided list of regex strings.
        compiledRegexList = list()
        for regexString in importRegexList:
            compiledRegexList.append(re.compile(importBegin + regexString))

        # Bucketize the import statements by their matching regex.
        for compiledRegex in compiledRegexList:
            for importStatement in importStatements:
                if compiledRegex.match(importStatement):
                    regexSortedList.append(importStatement)

    # If the regex list was empty, the sorted list is the answer.
    else:
        regexSortedList = importStatements

    return regexSortedList

# Given a list of import statements, divide it into top, static and normal
# imports.
def separateImports(importStatements):
    global importTopImpList
    global importMiddleList
    global importStaticList

    # Get list of Static Imports.
    regexStaticImports = ["static\s+"]
    importStaticList = extractImportsGivenRegexList(importStatements, regexStaticImports)

    # Get list of Static Imports.
    regexTopImports = topImports
    importTopImpList = extractImportsGivenRegexList(importStatements, regexTopImports)

    # Anything remaining is a Middle Import.
    importMiddleList = importStatements

# Return a list of all import statements from the buffer.  Set globals which
# denote the beginning and end of the range of import statements.
def extractImports():
    global importBegin
    global rangeStart
    global rangeEnd

    rangeStart = -1
    rangeEnd = -1
    
    importStatements = list()
    
    # Compile the Regex to Match Middle Import Statements.
    regexBeginningOfImportStatment = re.compile(importBegin)

    # Find All Import Statements.
    lastMatch = -1
    for lineNum, line in enumerate(vim.current.buffer):
        if (regexBeginningOfImportStatment.match(line)):
            # Indicate the Start of the Import Statement Range if not yet set.
            if rangeStart == -1:
                rangeStart = lineNum
    
            lastMatch = lineNum
            # Add the matching import to the list.
            importStatements.append(line)

    # Indicate the End of the Import Statement Range.
    rangeEnd = lastMatch
    
    return importStatements

# Return a list of matching imports given a list of import statements and a
# list of regular expression strings.
def extractImportsGivenRegexList(importStatements, importRegexList):
    global importBegin
    matchingImportsList = list()

    # Precompile the regexes from the provided list of regex strings.
    compiledRegexList = list()
    for regexString in importRegexList:
        compiledRegexList.append(re.compile(importBegin + regexString))

    # Iterate over the provided list of import statements.
    for importStatement in list(importStatements):

        # Iterate over each of the compiled regexes.
        for compiledRegex in compiledRegexList:

            # If the import statement matches the regex,
            if compiledRegex.match(importStatement):
                # Add the matching import to the list.
                matchingImportsList.append(importStatement)

                # Remove the matching import from the provided list.
                importStatements.remove(importStatement)

                # The import statement matches, no need to continue checking
                # against more regexes.
                break

    return matchingImportsList

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
def insertSpacing(importStatements, depth):
    # Copy the importStatements into a separate variable so that we are not iterating
    # over the list we are editing.
    spacedList = list(importStatements)

    # Review each entry of the list, if a separator is required, insert it.
    row = 0
    prevImport = ""
    currImport = ""
    for currImport in importStatements:
        if not prevImport:
            prevImport = currImport

        if isSeparatorRequired(prevImport, currImport, depth):
            spacedList.insert(row, "")
            row += 1

        prevImport = currImport
        row += 1

    # Remove Last Blank Entry (if present)
    if len(spacedList) and not spacedList[-1]:
        del spacedList[-1]

    # Replace the import list with our spaced out copy.
    importStatements = spacedList

    return importStatements

def deleteRange(start, end):
    # Remove Existing Imports from the Buffer.
    del vim.current.buffer[start:end + 2]

# Insert a list of lines into the buffer at the provided start line.
def insertListAtLine(startLine, lineList):
    # Do not append an empty list since this will insert an additional newline.
    if len(lineList):

        # Append the Sorted List to the Buffer.
        # If start line is before the beginning of the file, prepend the list
        # to the buffer.
        if startLine < 0:
            vim.current.buffer[0:0] = lineList
        # Otherwise, append the list below the provided startLine.
        else:
            # Append the Sorted List to the Buffer.
            vim.current.buffer.append(lineList, startLine)

    # Return Cursor Position After Inserted Lines.
    return startLine + len(lineList)

# Update the Buffer with the fully sorted list of import statements, adding
# empty lines as configured.
def updateBuffer(fullySortedImportStatements):
    global rangeStart
    global rangeEnd

    # Remove the range of imports.
    deleteRange(rangeStart, rangeEnd)

    # Insert Spacing into Middle Import List.
    formattedList  = insertSpacing(fullySortedImportStatements, depth)

    startLine = rangeStart - 1

    startLine = insertListAtLine(startLine, formattedList)

    # Insert a newline at the end.
    startLine = insertListAtLine(startLine, [""])

# Parse out the Import Statements.
parseImports()

# Update the Buffer with the Sorted Import Statements.
updateBuffer(sortImports())
