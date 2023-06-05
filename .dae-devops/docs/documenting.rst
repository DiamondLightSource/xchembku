.. # ********** Please don't edit this file!
.. # ********** It has been generated automatically by dae_devops version 0.5.3.
.. # ********** For repository_name xchembku

Documenting
=======================================================================

If you plan to make update the documentation in this repository, you can use the steps below.

First, follow the steps in the Developing section to get a copy of the source code and install its dependencies.

If you didn't do this already, make sure you have the documentation tools::

    $ cd <your development area>/xchembku
    $ pip install -e .[docs]

To produce the documentation locally::

    $ tox -q -e docs

This writes the html into local directory build/html.  You can browse the local documentation by::

    file:///<your development area>/xchembku/build/html/index.html

When you push either the main branch or a tag to GitHub, the documents are built and published automatically to this url::

    https://diamondlightsource.github.io/xchembku/main/index.html


.. # dae_devops_fingerprint 863eadb28713e672ac42c9886c928db0
