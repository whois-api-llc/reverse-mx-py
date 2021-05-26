from json import loads, JSONDecodeError
import re
from ipaddress import IPv4Address, AddressValueError

from .net.http import ApiRequester
from .models.response import Response
from .exceptions.error import ParameterError, EmptyApiKeyError, \
    UnparsableApiResponseError


class Client:
    __default_url = "https://reverse-mx.whoisxmlapi.com/api/v1"
    _api_requester: ApiRequester or None
    _api_key: str

    _re_api_key = re.compile(r'^at_[a-z0-9]{29}$', re.IGNORECASE)
    _domain_name = re.compile(r'^([a-z0-9_][-_a-z0-9]{0,62}\.){1,32}[0-9a-z][-0-9a-z]{1,62}')
    _SUPPORTED_FORMATS = ['json', 'xml']

    _PARSABLE_FORMAT = 'json'

    JSON_FORMAT = 'JSON'
    XML_FORMAT = 'XML'

    def __init__(self, api_key: str, **kwargs):
        """
        :param api_key: str: Your API key.
        :key base_url: str: (optional) API endpoint URL.
        :key timeout: float: (optional) API call timeout in seconds
        """

        self._api_key = ''

        self.api_key = api_key

        if 'base_url' not in kwargs:
            kwargs['base_url'] = Client.__default_url

        self.api_requester = ApiRequester(**kwargs)

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = Client._validate_api_key(value)

    @property
    def api_requester(self) -> ApiRequester or None:
        return self._api_requester

    @api_requester.setter
    def api_requester(self, value: ApiRequester):
        self._api_requester = value

    @property
    def base_url(self) -> str:
        return self._api_requester.base_url

    @base_url.setter
    def base_url(self, value: str or None):
        if value is None:
            self._api_requester.base_url = Client.__default_url
        else:
            self._api_requester.base_url = value

    @property
    def timeout(self) -> float:
        return self._api_requester.timeout

    @timeout.setter
    def timeout(self, value: float):
        self._api_requester.timeout = value

    def iterate_pages(self, mx: str or IPv4Address):
        """
        Iterate over all pages of domains related to given MX

        :param str|IPv4Address mx: MX server name
        :yields Response: Instance of `Response` with a page.
        :raises ConnectionError:
        :raises ReverseMxApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        """

        resp = self.data(mx)
        yield resp
        while resp.has_next():
            resp = self.next_page(mx, resp)
            yield resp

    def next_page(self, mx: str or IPv4Address, current_page: Response) \
            -> Response:
        """
        Get the next page if available, otherwise returns the given one

        :param str|IPv4Address mx: MX server name
        :param Response current_page: The current page.
        :return: Instance of `Response` with a next page.
        :raises ConnectionError:
        :raises ReverseMxApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        """

        if current_page.size > 0:
            last_domain = current_page.result[-1].name
            return self.data(mx, search_from=last_domain)
        return current_page

    def data(self, mx: str or IPv4Address, **kwargs) -> Response:
        """
        Get parsed API response as a `Response` instance.

        :param str|IPv4Address mx: MX server (domain or IP address).
        :key search_from: Optional. The domain name which is used as an
                offset for the results returned.
        :return: `Response` instance
        :raises ConnectionError:
        :raises ReverseMxApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        """

        kwargs['response_format'] = Client._PARSABLE_FORMAT

        response = self.raw_data(mx, **kwargs)
        try:
            parsed = loads(str(response))
            if 'result' in parsed:
                return Response(parsed)
            raise UnparsableApiResponseError(
                "Could not find the correct root element.", None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError("Could not parse API response", error)

    def raw_data(self, mx: str or IPv4Address, **kwargs) -> str:
        """
        Get raw API response.

        :param str|IPv4Address mx: MX server (domain or IP address).
        :key search_from: Optional. The domain name which is used as an
                offset for the results returned.
        :key response_format: Optional. use constants
                JSON_FORMAT and XML_FORMAT
        :return: str
        :raises ConnectionError:
        :raises ReverseMxApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        """

        if self.api_key == '':
            raise EmptyApiKeyError('')

        mx = Client._validate_mx_server(mx, True)

        if 'output_format' in kwargs:
            kwargs['response_format'] = kwargs['output_format']
        if 'response_format' in kwargs:
            response_format = Client._validate_response_format(
                kwargs['response_format'])
        else:
            response_format = Client._PARSABLE_FORMAT

        if 'search_from' in kwargs:
            search_from = Client._validate_search_from(kwargs['search_from'])
        else:
            search_from = "0"

        return self._api_requester.get(self._build_payload(
            mx,
            search_from,
            response_format
        ))

    @staticmethod
    def _validate_api_key(api_key) -> str:
        if Client._re_api_key.search(
                str(api_key)
        ) is not None:
            return str(api_key)
        else:
            raise ParameterError("Invalid API key format.")

    @staticmethod
    def _validate_mx_server(value: str or IPv4Address, required=False) -> str:
        if value is None:
            raise ParameterError("MX could be a None value")

        if isinstance(value, IPv4Address):
            return str(value)

        if type(value) is not str:
            raise ParameterError('MX should be a string or IPv4Address')

        if Client._domain_name.search(value) is not None:
            return value
        try:
            IPv4Address(value)
            return value
        except AddressValueError:
            pass

        raise ParameterError("Invalid MX name parameter")

    @staticmethod
    def _validate_search_from(value):
        if type(value) is str and len(value) > 0:
            return value
        raise ParameterError("Invalid search_from parameter")

    @staticmethod
    def _validate_response_format(_format: str):
        if _format.lower() in Client._SUPPORTED_FORMATS:
            return str(_format)
        else:
            raise ParameterError(
                "Output format should be either JSON or XML.")

    def _build_payload(self, mx, search_from, response_format):
        return {
            'apiKey': self.api_key,
            'mx': mx,
            'from': search_from,
            'outputFormat': response_format
        }
