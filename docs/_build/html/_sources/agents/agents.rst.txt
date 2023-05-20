Agents
======

Agents are the core idea of OSNAP. This section of documentation contains discussions about `what agents are <./what_are_agents.html>`_, how to create OSNAP agents, and more. 

Simply put, an agent only has to implement the following contract:

- Expose it's metadata via an **info** method
- Accept incoming requests via a **run** method
- Listen for incoming messages via a **listen** method
- Complete objectives or tasks with a **complete** method
- Terminate objectives or tasks with a **terminate** method

For a more abstract deep dive into agents: 

.. toctree::
   :maxdepth: 1

   agent_basics.ipynb
   what_are_agents.ipynb
