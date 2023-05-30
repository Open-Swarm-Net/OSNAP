from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from osnap_client.managers import SwarmManagerBase
from osnap_client.agents import SwarmAgentBase

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
    def retrieve_agent_information(self, agent_id: str) -> Optional[SwarmAgentBase]:
        """
        Retrieve the information of a specific Agent from the registry.

        Args:
            agent_id (str): Unique identifier of the Agent.

        Returns:
            SwarmAgentBase: Instance of SwarmAgentBase representing the retrieved Agent, or None if not found.
        """