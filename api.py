import requests
from requests.exceptions import ReadTimeout, RequestException
from typing import Optional, Dict, Any

class KufarAPI:
    """Handles all Kufar.by API interactions"""
    
    BASE_URL = "https://www.kufar.by"
    API_URL = "https://api.kufar.by"
    STATS_URL = "https://statpoints.kufar.by"
    CRE_URL = "https://cre-api.kufar.by"
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
    
    # Common headers shared across requests
    COMMON_HEADERS = {
        "User-Agent": USER_AGENT,
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "Priority": "u=4",
        "Host": "api.kufar.by",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-type": "application/json",
        "g-recaptcha-response": "",
        "X-App-Name": "Web Kufar",
        "X-Pulse-Environment-Id": "6bc55ac4-4edd-4d5e-8f24-f188ac377de7",
        "X-Rudder-Anonymous-Id": "6bc55ac4-4edd-4d5e-8f24-f188ac377de7",
        "X-App-Request-Source": "ad_view",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers"
    }
    
    def __init__(self, token: str):
        self.token = token
        self.simple_headers = {"User-Agent": self.USER_AGENT}
        self.auth_headers = {**self.COMMON_HEADERS, "Authorization": token}
    
    def get_listings_page(self) -> Optional[str]:
        """Fetch the main listings page"""
        try:
            response = requests.get(f"{self.BASE_URL}/l", headers=self.simple_headers)
            response.encoding = "utf-8"
            return response.text
        except RequestException as e:
            print(f"Failed to fetch listings page: {e}")
            return None
    
    def get_phone_number(self, item_id: str) -> str:
        """Fetch phone number for a specific listing"""
        try:
            # Make all required requests
            self._make_phone_requests(item_id)
            
            phone_req = requests.get(
                f"{self.API_URL}/search-api/v2/item/{item_id}/phone",
                headers=self.auth_headers,
                timeout=10
            )
            
            return self._parse_phone_response(phone_req.json())
        except ReadTimeout:
            return "Timeout"
        except RequestException as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def _make_phone_requests(self, item_id: str) -> None:
        """Make supporting requests for phone number access"""
        phone_url = f"{self.API_URL}/search-api/v2/item/{item_id}/phone"
        stats_url = f"{self.STATS_URL}/v1/statpoints/increment?ad={item_id}&statpoint=phoneview"
        cre_url = f"{self.CRE_URL}/fb-event-broker/v1/event"
        
        # Fire and forget requests - we don't need responses
        requests.options(phone_url, headers=self.COMMON_HEADERS, timeout=5)
        requests.put(stats_url, headers=self.COMMON_HEADERS, timeout=5)
        requests.options(stats_url, headers=self.COMMON_HEADERS, timeout=5)
        requests.options(cre_url, headers=self.COMMON_HEADERS, timeout=5)
        requests.post(cre_url, headers=self.auth_headers, timeout=5, data={
            "event_name": "Generalist_call_click",
            "event_id": "7535499026424987",
            "action_source": "website",
            "event_source_url": f"{self.BASE_URL}/item/{item_id}?searchId=4e6e01c4-ef44-462e-b1f0-eda88e65fc5d&r_block=Previously%20Viewed"
        })
    
    def _parse_phone_response(self, response_json: Dict[str, Any]) -> str:
        """Parse phone number from API response"""
        error = response_json.get("error")
        if error:
            if isinstance(error, dict) and error.get("message"):
                return f"Error: {error['message']}"
            return f"Error: {error}"
        
        phone = response_json.get("phone")
        return phone if phone else "Undefined"
    
    def get_item_description(self, item_id: str) -> str:
        """Fetch and parse item description"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/item/{item_id}",
                headers=self.simple_headers,
                timeout=10
            )
            response.encoding = "utf-8"
            return self._parse_description(response.text)
        except RequestException as e:
            print(f"Failed to fetch description for item {item_id}: {e}")
            return "Undefined"
    
    def _parse_description(self, html: str) -> str:
        """Parse item description from HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "html.parser")
        description_parts = []
        
        # Find parameters block
        param_div = soup.find("div", {"data-name": lambda x: x and "parameters-block" in x})
        if param_div:
            h2 = param_div.find("h2")
            if h2:
                description_parts.append(h2.text)
            
            # Parse parameters
            labels = param_div.find_all("div", class_=lambda x: x and "styles_parameter_label" in x)
            values = param_div.find_all("div", class_=lambda x: x and "styles_parameter_value" in x)
            
            for label, value in zip(labels, values):
                description_parts.append(f"{label.text} {value.text}")
        
        # Find description
        desc_div = soup.find("div", {"itemprop": "description"})
        if desc_div:
            desc_text = desc_div.prettify()
            desc_text = desc_text.replace('<div itemprop="description">', "")
            desc_text = desc_text.replace('</div>', "")
            desc_text = desc_text.replace('<br/>', "\n")
            description_parts.append(desc_text.rstrip())
        
        return "\n".join(description_parts) if description_parts else "Undefined"