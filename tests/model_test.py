import time
import unittest
from json import loads
from reversemx import Response, ErrorMessage


_json_response_ok = '''{
   "result": [
      {
         "name": "mabizsolution.com",
         "first_seen": "1530901800",
         "last_visit": "1530901800"
      },
      {
         "name": "jakafajnadomena.pl",
         "first_seen": "1530905127",
         "last_visit": "1530905127"
      },
      {
         "name": "teenchallengetm.ro",
         "first_seen": "1530487091",
         "last_visit": "1531103210"
      },
      {
         "name": "chu.com.br",
         "first_seen": "1530907559",
         "last_visit": "1530907559"
      },
      {
         "name": "improveshoppingcart.com",
         "first_seen": "1530497143",
         "last_visit": "1531114542"
      }
   ],
   "current_page": 1,
   "size": 5
}'''

_json_response_error = '''{
    "code": 403,
    "messages": "Access restricted. Check credits balance or enter the correct API key."
}'''


class TestModel(unittest.TestCase):

    def test_response_parsing(self):
        response = loads(_json_response_ok)
        parsed = Response(response)
        self.assertEqual(parsed.size, response['size'])
        self.assertIsInstance(parsed.result, list)
        self.assertEqual(
            parsed.result[0].name,
            response['result'][0]['name'])
        self.assertEqual(
            time.mktime(parsed.result[0].first_seen.timetuple()),
            float(response['result'][0]['first_seen']))
        self.assertEqual(
            time.mktime(parsed.result[0].last_visit.timetuple()),
            float(response['result'][0]['last_visit']))

        self.assertEqual(
            parsed.result[1].name,
            response['result'][1]['name'])
        self.assertEqual(
            time.mktime(parsed.result[1].first_seen.timetuple()),
            float(response['result'][1]['first_seen']))
        self.assertEqual(
            time.mktime(parsed.result[1].last_visit.timetuple()),
            float(response['result'][1]['last_visit']))

    def test_error_parsing(self):
        error = loads(_json_response_error)
        parsed_error = ErrorMessage(error)
        self.assertEqual(parsed_error.code, error['code'])
        self.assertEqual(parsed_error.message, error['messages'])
