from container.docker.utils import which_docker


def test_which_docker():
    assert which_docker() is not None
