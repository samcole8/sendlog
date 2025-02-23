import unittest
from unittest.mock import patch, MagicMock
from utils.config_handler import ConfigHandler

class TestConfigHandler(unittest.TestCase):

    @patch('builtins.open', create=True)
    @patch('yaml.safe_load')
    def test_get_data(self, mock_safe_load, mock_open):
        mock_safe_load.return_value = {
            "files": {
                "/var/auth.log": {
                    "plugin": "myplugin",
                    "format": "MyLog",
                    "rules": {
                        "MyRule": {
                            "transformations": {
                                "MyTransformation": {
                                    "endpoints": ["myendpoint"]
                                },
                                "MyOtherTransformation": {
                                    "endpoints": ["myendpoint3"]
                                }
                            }
                        }
                    }
                },
                "/var/app.log": {
                    "plugin": "appplugin",
                    "format": "MyLog",
                    "rules": {
                        "AppRule": {
                            "transformations": {
                                "AppTransformation": {
                                    "endpoints": ["appendpoint1", "appendpoint2"]
                                }
                            }
                        }
                    }
                },
                "/var/transaction.log": {
                    "plugin": "transactionplugin",
                    "format": "MyLog",
                    "rules": {
                        "TransactionRule": {
                            "transformations": {
                                "TransactionTransformation": {
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
        data = list(config_handler.get_data())
        expected_data = [
            ('/var/auth.log', 'myplugin', 'MyLog' ,'MyRule', 'MyTransformation', 'myendpoint'),
            ('/var/auth.log', 'myplugin', 'MyLog' ,'MyRule', 'MyOtherTransformation', 'myendpoint3'),
            ('/var/app.log', 'appplugin', 'MyLog' ,'AppRule', 'AppTransformation', 'appendpoint1'),
            ('/var/app.log', 'appplugin', 'MyLog' ,'AppRule', 'AppTransformation', 'appendpoint2'),
            ('/var/transaction.log', 'transactionplugin', 'MyLog' , 'TransactionRule', 'TransactionTransformation', 'transendpoint1'),
            ('/var/transaction.log', 'transactionplugin', 'MyLog' ,'TransactionRule', 'TransactionTransformation', 'transendpoint2')
        ]
        self.assertEqual(data, expected_data)
        mock_open.assert_called_with("test_config.yml", "r")
        mock_safe_load.assert_called_once()

if __name__ == "__main__":
    unittest.main()
