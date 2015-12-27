# Given a list of imports and depth sorting parameter, apply spacing to the
# list.
class Spacer:
    def __init__(self, spacingDepth):
        self._spacingDepth = spacingDepth

    # Insert spacing into a sorted list of imports.
    def getSpacedList(self, sortedImportList):
        # Copy the sortedImportList into a separate variable so that we are not iterating
        # over the list we are editing.
        spacedList = list(sortedImportList)

        # Review each entry of the list, if a separator is required, insert it.
        row = 0
        prevImport = ""
        currImport = ""
        for currImport in sortedImportList:
            if not prevImport:
                prevImport = currImport

            if self._isSeparatorRequired(prevImport, currImport):
                spacedList.insert(row, "")
                row += 1

            prevImport = currImport
            row += 1

        # Remove Last Blank Entry (if present)
        if len(spacedList) and not spacedList[-1]:
            del spacedList[-1]

        return spacedList

    # Determine if a separator is required between the two provided imports, given
    # a depth into the imports to check.  Depth is the number of package levels to
    # check (i.e. the number of dots in the import statement).
    def _isSeparatorRequired(self, prevImport, currImport):
        prevList = prevImport.split(".", self._spacingDepth)
        currList = currImport.split(".", self._spacingDepth)

        del prevList[-1]
        del currList[-1]

        return prevList != currList
