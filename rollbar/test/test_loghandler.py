"""
Tests for the RollbarHandler logging handler
"""
import json
import logging
import mock
import sys

import rollbar
from rollbar.logger import RollbarHandler

from rollbar.test import BaseTest


_test_access_token = 'aaaabbbbccccddddeeeeffff00001111'
_test_environment = 'test'


class LogHandlerTest(BaseTest):
    def setUp(self):
        rollbar.DEFAULT_ROLLBAR = None

    def _create_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        rollbar_handler = RollbarHandler(_test_access_token, _test_environment)
        rollbar_handler.setLevel(logging.WARNING)

        logger.addHandler(rollbar_handler)

        return logger

    @mock.patch('rollbar.Rollbar.send_payload')
    def test_message_stays_unformatted(self, send_payload):
        logger = self._create_logger()
        logger.warning("Hello %d %s", 1, 'world')

        payload = json.loads(send_payload.call_args[0][0])

        self.assertEqual(payload['data']['body']['message']['body'], "Hello %d %s")
        self.assertEqual(payload['data']['body']['message']['args'], [1, 'world'])
        self.assertEqual(payload['data']['body']['message']['record']['name'], __name__)

    def test_request_is_get_from_log_record_if_present(self):
        logger = self._create_logger()
        # Request objects vary depending on python frameworks or packages.
        # Using a dictionary for this test is enough.
        request = {"fake": "request", "for":  "testing purporse"}

        # No need to test request parsing and payload sent,
        # just need to be sure that proper rollbar function is called
        # with passed request as argument.
        with mock.patch("rollbar.Rollbar.report_message") as report_message_mock:
            logger.warning("Warning message", extra={"request": request})
            self.assertEqual(report_message_mock.call_args[0][2], request)

        # Python 2.6 doesnt support extra param in logger.exception.
        if not sys.version_info[:2] == (2, 6):
            with mock.patch("rollbar.Rollbar.report_exc_info") as report_exc_info:
                logger.exception("Exception message", extra={"request": request})
                self.assertEqual(report_exc_info.call_args[0][1], request)
