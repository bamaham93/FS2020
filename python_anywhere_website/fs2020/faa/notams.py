from credentials.faa import client_id, client_secret
import requests

example_request_mock = f"""
https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/0a116119-6959-40fa-99a9-3fb00de324a5/notam-api/1.0.4/m/notams?responseFormat=geoJson&icaoLocation=KCNI&pageNum=1%client_id={client_id}%client_secret={client_secret}
"""

example_request_prod = """
https://external-api.faa.gov/notamapi/v1/notams?
icaoLocation=KCNI
&pageNum=1
"""

class NOTAMS:
    """
    FAA Notices To Airmen.
    """

    def __init__(self):
        """
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def _get(self, url: str):
        """
        """
        return requests.get(url)



    def get_airport_notams(self):
        """
        Gets NOTAMs that apply to, or are listed by, airport.
        """
        result = self._get(example_request_mock)
        return result
