from JavaImp.Spacer import Spacer
from JavaImp.Sorter import Sorter
from JavaImp.Vim    import Vim

# Initialize Vim Helper
vim = Vim()

# Read in Configuration Options
depth = int(vim.getSetting("g:JavaImpSortPkgSep"))
topImports = vim.getSetting("g:JavaImpTopImports")
bottomImports = vim.getSetting("g:JavaImpBottomImports")
staticFirst = int(vim.getSetting("g:JavaImpStaticImportsFirst"))

# Initialize Spacer (which can insert spacing in between imports)
spacer = Spacer(depth)

sorter = Sorter(vim, spacer, topImports, bottomImports, staticFirst)
