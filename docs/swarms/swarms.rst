Swarms
==================

If it's the Open **SWARM** Network Agent Protocol, what is a swarm anyway? 
Simply put, a swarm is a group of one or more agents. Think about it like bees: 
there is a hive of bees, and each bee is an agent. The hive is the swarm. 

Why Swarms? 
##################

We think that a swarm of agents is more than the sum of it's parts. If we look
at the biological world for inspiration, `we can see <https://en.wikipedia.org/wiki/Swarm_behaviour>`_ that even simple organisms 
can do amazing things when they work together. We want to unlock the potential 
of swarms for emergent superintelligence, while providing a protocol that allows
us to do so efficiently, extensibly, and securely.

Design Rationale: Jobs of a Swarm 
##################

Let's continue with the analogy of the bee hive and thing about the basic functions
that a swarm needs to do: 

Design Principle 1
******************
The hive has rules for making new bees. If it senses the queen's pheromones, are 
dwindling, it will start making a new queen. 

**Job 1: Allow agents to join and leave the swarm, 
and to know who is in the swarm.**

Design Principle 2
******************
Bees communicate through a complex mechanism including `movement <https://www.youtube.com/watch?v=eKV7PiRTuSg>`_ and `pheromones <https://www.ncbi.nlm.nih.gov/books/NBK200983/#:~:text=In%20honey%20bees%2C%20as%20in,both%20developmental%20and%20behavioral%20changes.>`_. 
These are the "primitives" that allow the swarm to communicate about internal events, 
like a queen dying, or external events, like a new flower blooming. 

**Job 2: Allow agents to communicate with each other within the swarm and with the outside world.**

Design Principle 3
******************
Bees of course have a hive. The hive isn't the swarm, in fact they will 
periodically go `look for a new hive <https://blogs.ifas.ufl.edu/wakullaco/2019/03/18/swarming-is-a-sign-of-bees-looking-for-a-new-home/#:~:text=Soon%20scout%20worker%20honeybees%20begin,location%20for%20the%20new%20nest.>`_.
Instead, the hive is a place where the swarm can store food, raise young, and get
protection from the outside world.

**Job 3: Allow agents to store data, and to protect that data from the outside world.**

Design Principle 4
******************
Overall, all of the above principles are a means to an end: the swarm needs to
survive. If the swarm dies, the agents die. The complex mechanisms of the swarm
have devloped over at least 65 million years of evolution, and we don't have the 
benefit of that much time. Therefore we need to develop new mechanisms and rules 
to keep the swarm healthy and alive.

**Job 4: Keep the swarm healthy and alive.**


.. toctree::
    :maxdepth: 1

    how_swarms_work.md