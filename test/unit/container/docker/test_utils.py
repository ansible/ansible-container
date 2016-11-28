import unittest
import os
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

from container.docker.utils import which_docker, config_to_compose
from container.config import AnsibleContainerConfig

def get_base_path(project):
    return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         '..', '..', '..', 'integration', 'projects', project))

class TestAnsibleContainerDockerUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_which_docker(self):
        assert which_docker() is not None

    def test_config_to_compose_v2(self):
        # Test converting a compose version 2
        dir = get_base_path('postgres')
        config = AnsibleContainerConfig(base_path=dir)
        compose = config_to_compose(config)
        self.assertEqual(compose['version'], '2')
        self.assertIsInstance(compose['volumes'], dict)
        self.assertIsInstance(compose['services'], dict)

    def test_invalid_key(self):
        # Should detect invalid service keys
        dir = get_base_path('postgres')
        config = AnsibleContainerConfig(base_path=dir)
        config['services']['postgresql']['foo'] = 'bar'
        with self.assertRaises(Exception) as context:
            config_to_compose(config)
        self.assertTrue('invalid key' in str(context.exception))
