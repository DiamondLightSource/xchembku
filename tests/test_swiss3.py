import logging

import pytest

from xchembku_lib.crystal_plate_objects.swiss3 import Swiss3

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestSwiss3:
    """
    Test dataface interface by direct call.
    """

    def test(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        swiss3 = Swiss3({})

        position = swiss3.normalize_subwell_name("98ju_01A_1")
        assert position == "A01a"
        position = swiss3.normalize_subwell_name("98ju_08H_2")
        assert position == "H08c"
        position = swiss3.normalize_subwell_name("98ju_12H_3")
        assert position == "H12d"

        # Check invalid name formats.
        with pytest.raises(ValueError) as excinfo:
            swiss3.normalize_subwell_name("98ab_273A_1")
        assert "expected format" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            swiss3.normalize_subwell_name("98ju_01H_1.jpg")
        assert "expected format" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            swiss3.normalize_subwell_name("98ju_01J_1")
        assert "expected format" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            swiss3.normalize_subwell_name("98ju_01A_4")
        assert "expected format" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            swiss3.normalize_subwell_name("98j_01A_1")
        assert "expected format" in str(excinfo.value)
