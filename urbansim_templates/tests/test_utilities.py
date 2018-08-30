import pytest

from urbansim_templates import utils


def test_version_parse():
    assert utils.version_parse('0.1.0.dev0') == (0, 1, 0, 0)
    assert utils.version_parse('0.115.3') == (0, 115, 3, 0)
    assert utils.version_parse('3.1.dev7') == (3, 1, 0, 7)
    assert utils.version_parse('5.4') == (5, 4, 0, 0)
