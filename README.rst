=========================================
rax_default_network_flags_python_novaclient_ext
=========================================

Adds instance default networks extension support to python-novaclient.

This extension is autodiscovered once installed. To use::

    pip install rax_default_network_flags_python_novaclient_ext
    nova boot <usual args> --no-public --no-service-net
