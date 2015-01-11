import os
import vim
import plyj.parser
import plyj.model as m

# Set of All Referenced Types.  These are the types for which import statements
# should be generated.
allReferencedTypes = set()

# Visit all Types which are mentioned in variable, member and method
# declarations. Adds all non-primitive types to the set of All Referenced
# Types.
class TypeVisitor(m.Visitor):
    def __init__(self):
        super(TypeVisitor, self).__init__()

    def visit_Type(self, typ):
        # Indicates a primitive type.  Don't add it.
        if (isinstance(typ.name, str)):
            pass

        # Reference Type.  Add it to the set.
        else:
            typName = typ.name.value
            allReferencedTypes.add(typName)

# Swich to JavaImp's Data Directory so we can dump ply's debugging data.
oldDir = os.getcwd()
javaImpDataDir = vim.eval("g:JavaImpDataDir")
os.chdir(javaImpDataDir)

# Parse the File in the Current Buffer.
p = plyj.parser.Parser()
filepath = vim.eval("expand(\"%:p\")")
tree = p.parse_file(filepath)

# Visit all Types
tree.accept(TypeVisitor())

# Switch Back to the Previous Directory.
os.chdir(oldDir)

# TODO:
#
#      1. Find Method Target Types. (i.e. Naming.lookup(); 'Naming' is a reference type)
#      2. Find Object Castings. (i.e. MyBarType mbt = (MyBarType) foo;)
#      3. Find Enum Constant Types.  (i.e. Planets.MERCURY)
#      4. Don't include Inner Classes (i.e. no imports required).
#      5. Don't include built in types. (String, Integer, Object, etc)
# DONE 6. Optimize JavaImpInsert so that it can be run multiple times quickly.
# DONE 7. Control output of plyj temporary files.

for typ in allReferencedTypes:
    vim.command("call <SID>JavaImpInsert(0, \"" + typ + "\")")
    #print "call <SID>JavaImpInsert(1, \"" + typ + "\")"
