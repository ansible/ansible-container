import shutil
import tempfile
from os import path
import unittest
import os
import yaml

from container.config import AnsibleContainerConfig
from container.exceptions import AnsibleContainerConfigException


class TestAnsibleContainerConfig(unittest.TestCase):

    '''
    This test class creates a temporary folder with only "main.yml"
    written out. This tests passses if AnsibleContainerNotInitializedException
    is correctly raised due to a missing 'container.yml' file.
    '''

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.ansible_dir = path.join(self.test_dir, "ansible")
        os.mkdir(self.ansible_dir)
        # Create container.yml
        fs = open(os.path.join(self.ansible_dir,'container.yml'), 'w')
        fs.write('version: "1"\nservices:\n  web:\n    image: {{ web_image }}\n'
                 '    ports: {{ web_ports }}\n    command: ["sleep", "1d"]\n'
                 '    dev_overrides:\n      environment:\n        - DEBUG={{ debug }}\n'
                 '  db: {{ db_service }}\nregistries: {}\n')
        fs.close()
        # Create var file devel.yml
        fs = open(os.path.join(self.ansible_dir,'devel.yml'), 'w')
        fs.write('debug: 1\nweb_ports:\n  - 8000:8000\nweb_image: "busybox:latest"\ndb_service:\n'
                 '  image: postgres:9.5.4\n  expose:\n    - 5432\n  environment:\n    POSTGRES_DB_NAME: foobar\n'
                 '    POSTGRES_USER: admin\n    POSTGRES_PASSWORD: admin\n')
        fs.close()
        self.config = AnsibleContainerConfig(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_should_instantiate(self):
        self.assertEqual(len(self.config._config['services'].keys()), 2, 'Failed to load container.yml')

    def test_should_quote_template_vars(self):
        self.assertTrue(isinstance(self.config._config['services']['web']['image'], basestring),
                        'Failed to escape web.image.')
        self.assertTrue(isinstance(self.config._config['services']['web']['ports'], basestring),
                        'Failed to escape web.ports.')
        self.assertTrue(isinstance(self.config._config['services']['db'], basestring),
                        'Failed to escape db service.')

    def test_should_read_var_file(self):
        new_vars = self.config._get_variables_from_file('devel.yml')
        self.assertEqual(new_vars['debug'], 1, 'Failed to read and parse devel.yml')

    def test_should_raise_file_not_found_error(self):
        with self.assertRaises(AnsibleContainerConfigException) as exc:
            self.config._get_variables_from_file('foo')
        self.assertIn('Unable to locate', exc.exception.args[0])

    def test_should_read_environment_vars(self):
        os.environ.update({u'AC_DEBUG': '1'})
        new_vars = self.config._get_environment_variables()
        self.assertDictContainsSubset({u'debug': '1'}, new_vars)

    def test_should_get_defaults(self):
        # Create container.yml with defaults
        fs = open(os.path.join(self.ansible_dir, 'container.yml'), 'w')
        fs.write('version: "1"\ndefaults:\n  foo: bar\n  things:\n    - one\n    - two\n'
                 'services:\n  web:\n    image: {{ web_image }}\n'
                 '    ports: {{ web_ports }}\n    command: ["sleep", "1d"]\n'
                 '    dev_overrides:\n      environment:\n        - DEBUG={{ debug }}\n'
                 '  db: {{ db_service }}\nregistries: {}\n')
        fs.close()
        config = AnsibleContainerConfig(self.test_dir, ['devel.yml'])
        self.assertEqual(config._config.get('defaults', None), None, 'Failed to remove defaults.')
        self.assertDictContainsSubset({u'foo': 'bar'}, config._template_vars)
