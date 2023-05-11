.. OSNAP documentation master file, created by
   sphinx-quickstart on Mon May  8 15:59:08 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OSNAP: The Open Swarm Net Agent Protocol
========================================

OSNAP is a protocol for communication between agents. It includes: 

- Connection Management
- Agent Registration 
- Swarm Management
- Security and Authentication 
- Error Handling and Logging
- Extensibility

Where to Start?
---------------

If you're interested in exploring some of the big ideas behind OSNAP, 
check out:

- `Key Concepts <key_concepts/key_concepts.html>`_

If you just want to roll up your sleeves and try it out: 

- `Getting Started <getting_started/getting_started.html>`_

.. note:: 

   This project is still in an Alpha state, targeting a first public Beta
   
.. toctree::
   :maxdepth: 1
   :caption: Getting Started
   :hidden: 

   getting_started/getting_started.md

.. toctree::
   :maxdepth: 1
   :caption: Key Concepts 
   :name: key_concepts
   :hidden:

   agents/agents.rst
   swarms/swarms.rst

.. toctree::
   :maxdepth: 1
   :caption: Use cases
   :hidden:

   use_cases/use_cases.md

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
