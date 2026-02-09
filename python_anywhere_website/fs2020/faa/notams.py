# from credentials.faa import client_id, client_secret
import requests

try:
    from credentials.faa import client_id, client_secret
except ModuleNotFoundError:
    # from credentials.mock_faa_twilio import client_id, client_secret
    client_id = ""
    client_secret = ""

NOTAMS_API_URL = "https://external-api.faa.gov/notamapi/v1/notams"


class NOTAMS:
    """
    FAA Notices To Airmen.
    """

    def __init__(self):
        """ """
        self.client_id = client_id
        self.client_secret = client_secret

    def _get(self, url: str, params: dict | None = None):
        """Issue a GET request with optional query params."""
        return requests.get(url, params=params, timeout=15)

    def get_airport_notams(self, icao: str = "KCNI", page_num: int = 1):
        """Get NOTAMs for a single airport ICAO code."""
        params = {
            "icaoLocation": icao.strip().upper(),
            "pageNum": int(page_num),
        }
        result = self._get(NOTAMS_API_URL, params=params)
        if not result.ok:
            return {"error": result.text, "status": result.status_code}
        try:
            return result.json()
        except ValueError:
            return {"error": "Invalid JSON response", "raw": result.text}
