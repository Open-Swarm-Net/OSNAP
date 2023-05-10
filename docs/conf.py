# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OSNAP'
copyright = '2023, Forrest Murray'
author = 'Forrest Murray'
release = '0.1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.autodoc_pydantic",
    "myst_nb",
    "sphinx_copybutton",
    "sphinx_panels",
    "IPython.sphinxext.ipython_console_highlighting",
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"

html_theme_options = {
    "path_to_docs": "docs",
    "repository_url": "https://github.com/open-swarm-net/OSNAP",
    "use_repository_button": True,
}

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "open-swarm-net",  # Username
    "github_repo": "OSNAP",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}

## Notebooks configuration

nb_execution_mode = "off"
