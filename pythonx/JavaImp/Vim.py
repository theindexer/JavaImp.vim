import vim

class Vim:
    # Remove all lines from the current buffer within the provided range.
    def deleteRange(self, start, end):
        del vim.current.buffer[start:end + 2]

    # Retrieve the entire contents of the current Buffer.
    def retrieveBuffer(self):
        return vim.current.buffer

    # Insert a list of lines into the buffer at the provided start line.
    def insertListAtLine(self, startLine, lineList):
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

    # Retrieve a Vim Setting as a String.
    def getSetting(self, settingName):
        return vim.eval(settingName)
