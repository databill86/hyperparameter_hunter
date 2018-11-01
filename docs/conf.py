# -*- coding: utf-8 -*-
# Configuration file for the Sphinx documentation builder. This file does only contain a selection of the most common options.
# For a full list see the documentation: http://www.sphinx-doc.org/en/master/config

##################################################
# Path Setup
##################################################
# If extensions (or modules to document with autodoc) are in another directory, add these directories to sys.path here. If the
# directory is relative to the documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

##################################################
# Project Information
##################################################
project = "hyperparameter_hunter"
copyright = "2018, Hunter McGushion"
author = "Hunter McGushion"


def get_version():
    """Get the current version number for the library

    Returns
    -------
    String
        Of the form "<major>.<minor>.<micro>", in which "major", "minor" and "micro" are numbers"""
    with open("../hyperparameter_hunter/VERSION") as f:
        return f.read().strip()


version = ""  # The short X.Y version
release = get_version()  # The full version, including alpha/beta/rc tags

##################################################
# General Configuration
##################################################
# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.githubpages", "sphinx.ext.napoleon"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames. You can specify multiple suffix as a list of string: `source_suffix = ['.rst', '.md']`
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation for a list of supported languages. This is also used
# if you do content translation via gettext catalogs. Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

##################################################
# AutoDocumentation/Napoleon Settings
##################################################
autodoc_mock_imports = ["hyperparameter_hunter.utils.boltons_utils"]

autoclass_content = "init"  # 'both'
autodoc_member_order = "bysource"
autodoc_default_flags = ["show-inheritance"]


# add_module_names = False
# html_use_index = False
# html_copy_source = False
# html_show_sourcelink = False
html_split_index = False

napoleon_google_docstring = False
# napoleon_include_special_with_doc = True
napoleon_use_admonition_for_notes = False  # DEFAULT
# napoleon_use_param = True  # DEFAULT

##################################################
# Options for HTML Output
##################################################
# The theme to use for HTML and HTML Help pages. See the documentation for a list of builtin themes.
html_theme = "sphinx_rtd_theme"
# html_theme = 'nature'  # FLAG: ORIGINAL

# Theme options are theme-specific and customize the look and feel of a theme further. For a list of options available for each
# theme, see the documentation.
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here, relative to this directory. They are copied after
# the builtin static files, so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
# html_context = {'css_files': ['style.css']}
modindex_common_prefix = ["hyperparameter_hunter."]

# Custom sidebar templates, must be a dictionary that maps document names to template names. The default sidebars (for documents
# that don't match any pattern) are defined by theme itself. Builtin themes are using these templates by default:
# ``['localtoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html']``.
# html_sidebars = {}

##################################################
# Options for HTMLHelp Output
##################################################
# Output file base name for HTML help builder.
htmlhelp_basename = "hyperparameter_hunterdoc"

##################################################
# Options for LaTeX Output
##################################################
latex_elements = {
    # 'papersize': 'letterpaper',  # The paper size ('letterpaper' or 'a4paper')
    # 'pointsize': '10pt',  # The font size ('10pt', '11pt' or '12pt')
    # 'preamble': '',  # Additional stuff for the LaTeX preamble
    # 'figure_align': 'htbp',  # Latex figure (float) alignment
}

# Grouping the document tree into LaTeX files. List of tuples:
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "hyperparameter_hunter.tex",
        "hyperparameter\\_hunter Documentation",
        "Hunter McGushion",
        "manual",
    )
]

##################################################
# Options for Manual Page Output
##################################################
# One entry per manual page. List of tuples: (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, "hyperparameter_hunter", "hyperparameter_hunter Documentation", [author], 1)
]

##################################################
# Options for Texinfo Output
##################################################
# Grouping the document tree into Texinfo files. List of tuples:
# (source start file, target name, title, author, dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "hyperparameter_hunter",
        "hyperparameter_hunter Documentation",
        author,
        "hyperparameter_hunter",
        "One line description of project.",
        "Miscellaneous",
    )
]


def setup(app):
    app.add_stylesheet("style.css")
    # pass
