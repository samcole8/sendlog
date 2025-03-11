import unittest
from unittest.mock import patch, MagicMock
from config_handler import ConfigHandler

class TestConfigHandler(unittest.TestCase):

    @patch('builtins.open', create=True)
    @patch('yaml.safe_load')
    def test_files(self, mock_safe_load, mock_open):
        mock_safe_load.return_value = {
            "files": {
                "/var/auth.log": {
                    "plugin": "myplugin",
                    "log_type": "MyLogType",
                    "rules": {
                        "MyRule": {
                            "transformers": {
                                "MyTransformer": {
                                    "endpoints": ["myendpoint"]
                                },
                                "MyOtherTransformer": {
                                    "endpoints": ["myendpoint3"]
                                }
                            }
                        }
                    }
                },
                "/var/app.log": {
                    "plugin": "appplugin",
                    "log_type": "MyLogType",
                    "rules": {
                        "AppRule": {
                            "transformers": {
                                "AppTransformer": {
                                    "endpoints": ["appendpoint1", "appendpoint2"]
                                }
                            }
                        }
                    }
                },
                "/var/transaction.log": {
                    "plugin": "transactionplugin",
                    "log_type": "MyLogType",
                    "rules": {
                        "TransactionRule": {
                            "transformers": {
                                "TransactionTransformer": {
                                    "endpoints": ["transendpoint1", "transendpoint2"]
                                }
                            }
                        }
                    }
                }
            }
        }
        mock_open.return_value.__enter__.return_value = MagicMock()
        config_handler = ConfigHandler("test_config.yml")
        data = list(config_handler.files())
        expected_data = [
            ('/var/auth.log', 'myplugin', 'MyLogType' ,'MyRule', 'MyTransformer', 'myendpoint'),
            ('/var/auth.log', 'myplugin', 'MyLogType' ,'MyRule', 'MyOtherTransformer', 'myendpoint3'),
            ('/var/app.log', 'appplugin', 'MyLogType' ,'AppRule', 'AppTransformer', 'appendpoint1'),
            ('/var/app.log', 'appplugin', 'MyLogType' ,'AppRule', 'AppTransformer', 'appendpoint2'),
            ('/var/transaction.log', 'transactionplugin', 'MyLogType' , 'TransactionRule', 'TransactionTransformer', 'transendpoint1'),
            ('/var/transaction.log', 'transactionplugin', 'MyLogType' ,'TransactionRule', 'TransactionTransformer', 'transendpoint2')
        ]
        self.assertEqual(data, expected_data)
        mock_open.assert_called_with("test_config.yml", "r")
        mock_safe_load.assert_called_once()

if __name__ == "__main__":
    unittest.main()
