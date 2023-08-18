from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from osnap_client.managers import SwarmManagerBase, SwarmManager
from osnap_client.agents import SwarmAgentBase, SwarmAgent

class SwarmRegistryBase(ABC):
    @abstractmethod
    def add_swarm_entry(self, swarm: SwarmManagerBase):
        """
        Add the information of a joined Swarm to the registry.

        Args:
            swarm (SwarmManagerBase): Instance of SwarmManagerBase representing the joined Swarm.

        Returns:
            None
        """

    @abstractmethod
    def add_agent_entry(self, agent: SwarmAgentBase):
        """
        Add the information of an Agent to the registry.

        Args:
            agent (SwarmAgentBase): Instance of SwarmAgentBase representing the Agent.

        Returns:
            None
        """

    @abstractmethod
    def retrieve_swarm_information(self, swarm_id: str) -> Optional[SwarmManagerBase]:
        """
        Retrieve the information of a specific Swarm from the registry.

        Args:
            swarm_id (str): Unique identifier of the Swarm.

        Returns:
            SwarmManagerBase: Instance of SwarmManagerBase representing the retrieved Swarm, or None if not found.
        """

    @abstractmethod
    def retrieve_joined_agents(self, agent_id: str) -> List[SwarmAgent]:
        """
        Retrieve the information the Agents which have joined the registry.

        Returns:
            SwarmAgentBase: Instance of SwarmAgentBase representing the retrieved Agent, or None if not found.
        """

    @abstractmethod
    def join_swarm(self, from_entity: SwarmAgent | SwarmManager, to_entity: SwarmManager):
        """
        Add a relationship between a Swarm and an Agent or other Swarm to the registry.

        Args:
            from (SwarmAgentBase | SwarmManagerBase): Instance of SwarmAgentBase or SwarmManagerBase representing the source of the relationship.   
        """