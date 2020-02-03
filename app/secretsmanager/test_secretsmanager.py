import unittest
from app.secretsmanager.secretsmanager import parse_secrets_config


class ParseSecretsConfigTest(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        self.secrets = [
            {'Name': "test"},
            {'Name': "production/test"},
            {'Name': "production/test1"},
            {'Name': "staging/test2"},
            {'Name': "staging/test3"},
            {'Name': "dev"}
        ]

    # executed after each test
    def tearDown(self):
        pass

    def test_no_config(self):
        config = None
        test_config = [
            {
                "aws_secret_manager_name": "production/test",
                "namespace": "production",
                "secret_name": "test"
            },
            {
                "aws_secret_manager_name": "production/test1",
                "namespace": "production",
                "secret_name": "test1"
            },
            {
                "aws_secret_manager_name": "staging/test2",
                "namespace": "staging",
                "secret_name": "test2"
            },
            {
                "aws_secret_manager_name": "staging/test3",
                "namespace": "staging",
                "secret_name": "test3"
            },
        ]

        test_ignored = [
            {'Name': "test"},
            {'Name': "dev"}
        ]
        env_config, ignored = parse_secrets_config(config, self.secrets)

        self.assertListEqual(test_config, env_config)
        self.assertListEqual(ignored, test_ignored)

    def test_with_environment(self):
        config = {
            'secret_manager_envs': [
                {'name': 'production'}
            ]
        }
        test_config = [
            {
                "aws_secret_manager_name": "production/test",
                "namespace": "production",
                "secret_name": "test"
            },
            {
                "aws_secret_manager_name": "production/test1",
                "namespace": "production",
                "secret_name": "test1"
            },
        ]
        env_config, ignored = parse_secrets_config(config, self.secrets)
        self.assertListEqual(test_config, env_config)

    def test_multiple_namespaces(self):
        config = {
            'secret_manager_envs': [
                {
                    'name': 'production',
                    'namespaces': [
                        'namespace1',
                        'namespace2',
                    ]
                }
            ]
        }
        test_config = [
            {
                "aws_secret_manager_name": "production/test",
                "namespace": "namespace1",
                "secret_name": "test"
            },
            {
                "aws_secret_manager_name": "production/test",
                "namespace": "namespace2",
                "secret_name": "test"
            },
            {
                "aws_secret_manager_name": "production/test1",
                "namespace": "namespace1",
                "secret_name": "test1"
            },
            {
                "aws_secret_manager_name": "production/test1",
                "namespace": "namespace2",
                "secret_name": "test1"
            },
        ]
        env_config, ignored = parse_secrets_config(config, self.secrets)
        self.assertListEqual(test_config, env_config)

    def test_custom_secret(self):
        config = {
            'secret_manager_envs': [
                {
                    'name': 'production',
                    'namespaces': [
                        'namespace1',
                        'namespace2',
                    ]
                }
            ],
            'custom_secrets': [
                {
                    "aws_secret_manager_name": "customawsname",
                    "namespace": "customnamespace",
                    "secret_name": "customname",
                },
                {
                    "aws_secret_manager_name": "dev",
                    "namespace": "dev",
                    "secret_name": "dev",
                },
            ]
        }
        test_config = [
            {
                "aws_secret_manager_name": "production/test",
                "namespace": "namespace1",
                "secret_name": "test"
            },
            {
                "aws_secret_manager_name": "production/test",
                "namespace": "namespace2",
                "secret_name": "test"
            },
            {
                "aws_secret_manager_name": "production/test1",
                "namespace": "namespace1",
                "secret_name": "test1"
            },
            {
                "aws_secret_manager_name": "production/test1",
                "namespace": "namespace2",
                "secret_name": "test1"
            },
            {
                "aws_secret_manager_name": "customawsname",
                "namespace": "customnamespace",
                "secret_name": "customname"
            },
            {
                "aws_secret_manager_name": "dev",
                "namespace": "dev",
                "secret_name": "dev"
            },
        ]
        env_config, ignored = parse_secrets_config(config, self.secrets)

        # add check to see if dev is in ingnored secrets
        # {
        #     "aws_secret_manager_name": "dev",
        #     "namespace": "dev",
        #     "secret_name": "dev"
        # },

        self.assertListEqual(test_config, env_config)


if __name__ == '__main__':
    unittest.main()
