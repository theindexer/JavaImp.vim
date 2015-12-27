import re

class Sorter:
    IMPORT_BEGIN = "^\s*import\s+" 

    def __init__(self, vim, spacer, topImports, bottomImports, staticFirst):
        self._vim = vim
        self._spacer = spacer
        self._topImports = topImports
        self._bottomImports = bottomImports
        self._staticFirst = staticFirst

        # Initialize lists
        self._importTopImpList = []
        self._importMiddleList = []
        self._importBottomList = []
        self._importStaticList = []

        # Initialize Import Statement Range
        self._rangeStart = -1
        self._rangeEnd = -1

        # Parse out the Import Statements.
        self._parseImports()

        # Update the Buffer with the Sorted Import Statements.
        self._updateBuffer(self._sortImports())

    # Extract and Separate Imports.
    def _parseImports(self):
        self._separateImports(self._extractImports())

    def _sortImports(self):
        fullySortedImportStatements = list()

        # Sort Top Imports
        regexTopImports = self._topImports
        self._importTopImpList = self._regexSort(self._importTopImpList, regexTopImports)

        # Sort Middle Imports.
        self._importMiddleList = self._regexSort(self._importMiddleList, list())

        # Sort Bottom Imports.
        regexBottomImports = self._bottomImports
        self._importBottomList = self._regexSort(self._importBottomList, regexBottomImports)

        # Sort Static Imports.
        self._importStaticList = self._regexSort(self._importStaticList, list())

        # Add Static Imports first (if configured to do so)
        if self._staticFirst:
            fullySortedImportStatements.extend(self._importStaticList)

        # Add Top Imports
        fullySortedImportStatements.extend(self._importTopImpList)

        # Add Middle Imports
        fullySortedImportStatements.extend(self._importMiddleList)

        # Add Bottom Imports
        fullySortedImportStatements.extend(self._importBottomList)

        # Add Static Imports last (if configured to do so)
        if not self._staticFirst:
            fullySortedImportStatements.extend(self._importStaticList)

        return fullySortedImportStatements

    # Sort the provided importStatements first by the provided importRegexList, then
    # alphanumerically.
    def _regexSort(self, importStatements, importRegexList):
        regexSortedList = list()

        # First sort the list alphanumerically.
        importStatements.sort()

        # If the regex list is non-empty
        if len(importRegexList) > 0:
            # Precompile the regexes from the provided list of regex strings.
            compiledRegexList = list()
            for regexString in importRegexList:
                compiledRegexList.append(re.compile(self.IMPORT_BEGIN + regexString))

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
    def _separateImports(self, importStatements):
        # Get list of Static Imports.
        regexStaticImports = ["static\s+"]
        self._importStaticList = self._extractImportsGivenRegexList(importStatements, regexStaticImports)

        # Get list of Top Imports.
        regexTopImports = self._topImports
        self._importTopImpList = self._extractImportsGivenRegexList(importStatements, regexTopImports)

        # Get list of Bottom Imports.
        regexBottomImports = self._bottomImports
        self._importBottomList = self._extractImportsGivenRegexList(importStatements, regexBottomImports)

        # Anything remaining is a Middle Import.
        self._importMiddleList = importStatements

    # Return a list of all import statements from the buffer.  Set globals which
    # denote the beginning and end of the range of import statements.
    def _extractImports(self):
        self._rangeStart = -1
        self._rangeEnd = -1
        
        importStatements = list()
        
        # Compile the Regex to Match Middle Import Statements.
        regexBeginningOfImportStatment = re.compile(self.IMPORT_BEGIN)

        # Find All Import Statements.
        lastMatch = -1
        for lineNum, line in enumerate(self._vim.retrieveBuffer()):
            if (regexBeginningOfImportStatment.match(line)):
                # Indicate the Start of the Import Statement Range if not yet set.
                if self._rangeStart == -1:
                    self._rangeStart = lineNum
        
                lastMatch = lineNum
                # Add the matching import to the list.
                importStatements.append(line)

        # Indicate the End of the Import Statement Range.
        self._rangeEnd = lastMatch
        
        return importStatements

    # Return a list of matching imports given a list of import statements and a
    # list of regular expression strings.
    def _extractImportsGivenRegexList(self, importStatements, importRegexList):
        matchingImportsList = list()

        # Precompile the regexes from the provided list of regex strings.
        compiledRegexList = list()
        for regexString in importRegexList:
            compiledRegexList.append(re.compile(self.IMPORT_BEGIN + regexString))

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

    # Update the Buffer with the fully sorted list of import statements, adding
    # empty lines as configured.
    def _updateBuffer(self, fullySortedImportStatements):
        # Remove the range of imports.
        self._vim.deleteRange(self._rangeStart, self._rangeEnd)

        # Insert Spacing into Middle Import List.
        spacedList = self._spacer.getSpacedList(fullySortedImportStatements)

        startLine = self._rangeStart - 1

        startLine = self._vim.insertListAtLine(startLine, spacedList)

        # Insert a newline at the end.
        startLine = self._vim.insertListAtLine(startLine, [""])

