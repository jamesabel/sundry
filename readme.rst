Sundry
======

Miscellaneous Code

is_main()
---------

Instead of the not-so-pretty:

.. code-block:: python

    if __name__ == "__main__":
        main()


pip install `sundry` from PyPI:

.. code-block:: shell

    $pip install sundry

And use ``is_main()`` from `sundry`:

.. code-block:: python

    from sundry import is_main

    if is_main():
        main()

