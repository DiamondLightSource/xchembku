from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple


class Interface(ABC):
    """
    This is the required API interface for an Authorizer object.
    """

    @abstractmethod
    # ----------------------------------------------------------------------------------------
    def get_well_count(self) -> int:
        pass

    # ----------------------------------------------------------------------------------------
    @abstractmethod
    def normalize_subwell_name(self, subwell_name: str) -> str:
        """
        Converts the name given to the subwell by Luigi into the "position" format shown in soakdb3.

        Args:
            subwell_name (str): stem part of the subwell's image filename

        Raises:
            ValueError: the value does not follow the convention

        Returns:
            str: the displayable subwell position
        """
        pass

    # ----------------------------------------------------------------------------------------
    @abstractmethod
    def compute_drop_location_microns(
        self,
        crystal_well_record: Dict,
    ) -> Tuple[Optional[int], Optional[int]]:
        pass
