xchembku
=======================================================================

XChem Business Knowledge Unit.  Service, Client, API, persistent store.

Installation
-----------------------------------------------------------------------
::

    pip install xchembku

    xchembku --version

Documentation
-----------------------------------------------------------------------

See https://www.cs.diamond.ac.uk/xchembku for more detailed documentation.

Building and viewing the documents locally::

    git clone git+https://gitlab.diamond.ac.uk/scisoft/bxflow/xchembku.git 
    cd xchembku
    virtualenv /scratch/$USER/venv/xchembku
    source /scratch/$USER/venv/xchembku/bin/activate 
    pip install -e .[dev]
    make -f .xchembku/Makefile validate_docs
    browse to file:///scratch/$USER/venvs/xchembku/build/html/index.html

Topics for further documentation:

- TODO list of improvements
- change log


..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

