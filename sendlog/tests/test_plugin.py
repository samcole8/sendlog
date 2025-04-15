import unittest

from plugin import LogType, Rule, Transformer

class TestLogType(LogType):
    regex = r"\[(?P<timestamp>.*?)\] \[(?P<application>.*?)\] (?P<message>.*)"

class TestRule(Rule):
    regex = r"Running\s+'(?P<command>[^']+)'"

class TestTransformer(Transformer):
    def __call__(self, parts):
        context = parts["context"]
        return f"Command '{context['command']}' detected at {parts['timestamp']}."

class PluginTest(unittest.TestCase):
    def test_plugin_pipeline(self):
        log_line = "[2025-03-28T14:32:59+0000] [PACMAN] Running 'pacman -Syu'"

        expected_step1 = {
            "timestamp": "2025-03-28T14:32:59+0000",
            "application": "PACMAN",
            "message": "Running 'pacman -Syu'"
        }

        expected_step2 = {
            **expected_step1,
            "context": {"command": "pacman -Syu"}
        }

        expected_output = "Command 'pacman -Syu' detected at 2025-03-28T14:32:59+0000."

        testlogtype = TestLogType()
        testrule = TestRule()
        testtransformer = TestTransformer()

        parsed_log = testlogtype(log_line)
        enriched_log = testrule(parsed_log)
        final_output = testtransformer(enriched_log)

        self.assertEqual(parsed_log, expected_step1)
        self.assertEqual(enriched_log, expected_step2)
        self.assertEqual(final_output, expected_output)


if __name__ == "__main__":
    unittest.main()
