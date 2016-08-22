import shutil
import tempfile
from os import path
import unittest
import os
import yaml
import json

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
        # Create container.yml.
        container_text = (
            "version: '1'\n"
            "defaults:\n"
            "    web_image: apache:latest\n"
            "    web_ports: ['8080:80']\n"
            "    debug: 0\n"
            "    foo: bar\n"
            "services:\n"
            "    web:\n"
            "        image: {{ web_image }}\n"
            "        ports: {{ web_ports }}\n"
            "        command: ['sleep', '1d']\n"
            "        foo: {{ foo }}\n"
            "        dev_overrides:\n"
            "            environment: ['DEBUG={{ debug }}']\n"
            "    db: {{ db_service }}\n"
            "registries: {}\n"
        )
        with open(os.path.join(self.ansible_dir, 'container.yml'), 'w') as fs:
            fs.write(container_text)
        var_data = {
            "debug": 1,
            "web_ports": ["8000:8000"],
            "web_image": "python:2.7",
            "foo": "baz",
            "db_service": {
                "image": "python:2.7",
                "command": "sleep 10",
                "expose": [5432],
                "environment": {
                    "POSTGRES_DB_NAME": "foobar",
                    "POSTGRES_USER": "admin",
                    "POSTGRES_PASSWORD": "admin"
                }
            }
        }
        # Create var file devel.yml
        with open(os.path.join(self.ansible_dir, 'devel.yml'), 'w') as fs:
            yaml.safe_dump(var_data, fs, default_flow_style=False, indent=2)
        # create var file devel.txt
        with open(os.path.join(self.ansible_dir, 'devel.txt'), 'w') as fs:
            fs.write(json.dumps(var_data))
        self.config = AnsibleContainerConfig(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_should_instantiate(self):
        self.assertEqual(len(self.config._config['services'].keys()), 2, 'Failed to load container.yml')

    def test_should_quote_template_vars(self):
        config = self.config._read_config()
        self.assertTrue(isinstance(config['services']['web']['image'], basestring),
                        'Failed to escape web.image.')
        self.assertTrue(isinstance(config['services']['web']['ports'], basestring),
                        'Failed to escape web.ports.')
        self.assertTrue(isinstance(config['services']['db'], basestring),
                        'Failed to escape db service.')

    def test_should_remove_defaults_section(self):
        self.assertEqual(self.config._config.get('defaults', None), None, 'Failed to remove defaults.')

    def test_should_parse_defaults(self):
        self.config.var_file = None
        config = self.config._read_config()
        template_vars = self.config._get_variables(config)
        self.assertEqual(template_vars['web_image'], 'apache:latest')
        self.assertEqual(template_vars['debug'], 0)
        self.assertEqual(template_vars['foo'], 'bar')

    def test_should_parse_yaml_file(self):
        new_vars = self.config._get_variables_from_file('devel.yml')
        self.assertEqual(new_vars['debug'], 1, 'Failed to parse devel.yml - checked debug')
        self.assertEqual(new_vars['web_image'], "python:2.7", "Failed to parse devel.yml - web_image")

    def test_should_parse_json_file(self):
        new_vars = self.config._get_variables_from_file('devel.txt')
        self.assertEqual(new_vars['debug'], 1, 'Failed to parse devel.txt - checked debug')
        self.assertEqual(new_vars['web_image'], "python:2.7", "Failed to parse devel.txt - web_image")

    def test_should_raise_file_not_found_error(self):
        with self.assertRaises(AnsibleContainerConfigException) as exc:
            self.config._get_variables_from_file('foo')
        self.assertIn('Unable to locate', exc.exception.args[0])

    def test_should_read_environment_vars(self):
        os.environ.update({u'AC_DEBUG': '2'})
        new_vars = self.config._get_environment_variables()
        self.assertDictContainsSubset({u'debug': '2'}, new_vars)

    def test_should_give_precedence_to_env_vars(self):
        # If an environment var exists, it should get precedence.
        os.environ.update({u'AC_FOO': 'cats'})
        self.config.var_file = 'devel.yml'
        self.config.set_env('prod')
        self.assertEqual(self.config._config['services']['web']['foo'], 'cats')

    def test_should_give_precedence_to_file_vars(self):
        # If no environment var, then var defined in var_file should get precedence.
        if os.environ.get('AC_FOO'):
            del os.environ['AC_FOO']
        self.config.var_file = 'devel.yml'
        self.config.set_env('prod')
        self.assertEqual(self.config._config['services']['web']['foo'], 'baz')

    def test_should_give_precedence_to_default_vars(self):
        # If no environment var and no var_file, then the default value should be used.
        if os.environ.get('AC_FOO'):
            del os.environ['AC_FOO']
        self.config.var_file = None
        self.config.set_env('prod')
        self.assertEqual(self.config._config['services']['web']['foo'], 'bar')


