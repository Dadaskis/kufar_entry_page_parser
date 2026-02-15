import requests
from requests.exceptions import ReadTimeout, RequestException
from bs4 import BeautifulSoup
import traceback
import time
import random
from typing import Optional, Dict, Any
from dataclasses import dataclass
from lxml import etree
import os
from datetime import datetime

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

@dataclass
class Listing:
    """Data class representing a single listing"""
    title: str
    price: str = "Undefined"
    region: str = "Undefined"
    item_id: str = "Undefined"
    phone: str = "Undefined"
    description: str = "Undefined"
    
    def display(self) -> None:
        """Print listing information"""
        print(f"Title: {self.title}")
        print(f"Price: {self.price}")
        print(f"Region: {self.region}")
        print(f"ID: {self.item_id}")
        print(f"Phone: {self.phone}")
        print(f"Description: {self.description}")
        print("-" * 30)
        print("\n" * 3)
    
    def display_to_file(self, file_name) -> None:
        """Append displayed listing information to a file"""
        with open(file_name, "a", encoding="utf-8") as file:
            file.write(f"Title: {self.title}\n")
            file.write(f"Price: {self.price}\n")
            file.write(f"Region: {self.region}\n")
            file.write(f"ID: {self.item_id}\n")
            file.write(f"Phone: {self.phone}\n")
            file.write(f"Description: {self.description}\n")
            file.write("-" * 30 + "\n")
            file.write("\n" * 3 + "\n")
    
    def display_to_XML(self, file_name) -> None:
        """Append displayed listing information to XML file"""
        # Check if file exists
        if os.path.exists(file_name):
            # Parse existing XML
            tree = etree.parse(file_name)
            root = tree.getroot()
            
            # Update count attribute
            current_count = int(root.get('count', 0))
            root.set('count', str(current_count + 1))
        else:
            # Create new XML file with root
            root = etree.Element("listings")
            root.set("exported", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            root.set("count", "0")
            tree = etree.ElementTree(root)
        
        # Create new listing element
        listing_elem = etree.SubElement(root, "listing")
        listing_elem.set("id", str(len(root.findall('listing'))))
        listing_elem.set("item_id", self.item_id)
        
        # Add child elements
        etree.SubElement(listing_elem, "title").text = self.title
        etree.SubElement(listing_elem, "price").text = self.price
        etree.SubElement(listing_elem, "region").text = self.region
        etree.SubElement(listing_elem, "phone").text = self.phone
        
        # Handle description (CDATA for HTML content)
        desc_elem = etree.SubElement(listing_elem, "description")
        if self.description and self.description != "Undefined":
            if '<' in self.description and '>' in self.description:
                desc_elem.text = etree.CDATA(self.description)
            else:
                desc_elem.text = self.description
        
        # Write back to file
        tree.write(file_name, encoding='utf-8', pretty_print=True, xml_declaration=True)

class ListingParser:
    """Parses listings from HTML"""
    
    @staticmethod
    def extract_listings(html: str) -> list[Listing]:
        """Extract all listings from HTML"""
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        
        for section in soup.find_all("section"):
            listing = ListingParser._parse_section(section)
            if listing:
                listings.append(listing)
        
        return listings
    
    @staticmethod
    def _parse_section(section) -> Optional[Listing]:
        """Parse a single section into a Listing object"""
        h3_title = section.find("h3")
        if not h3_title:
            return None
        
        title = h3_title.text
        price = ListingParser._extract_price(section)
        region = ListingParser._extract_region(section)
        item_id = ListingParser._extract_item_id(section)
        
        return Listing(title=title, price=price, region=region, item_id=item_id)
    
    @staticmethod
    def _extract_price(section) -> str:
        """Extract price from section"""
        for span in section.find_all("span"):
            parent_class = span.parent.get("class")
            if parent_class and "styles_price" in str(parent_class):
                return span.text
        return "Undefined"
    
    @staticmethod
    def _extract_region(section) -> str:
        """Extract region from section"""
        for p in section.find_all("p"):
            p_class = p.get("class")
            if p_class and "styles_region" in str(p_class):
                return p.text
        return "Undefined"
    
    @staticmethod
    def _extract_item_id(section) -> str:
        """Extract item ID from section"""
        a_elem = section.find("a")
        if a_elem and a_elem.get("href"):
            link_url = a_elem.get("href").split("/")[-1]
            return link_url.split("?")[0]
        return "Undefined"

class KufarScraper:
    """Main scraper class coordinating the scraping process"""
    
    def __init__(self, token: str, delay_range: tuple = (10, 20)):
        self.api = KufarAPI(token)
        self.parser = ListingParser()
        self.delay_range = delay_range
    
    def scrape(self) -> None:
        """Main scraping method"""
        # Fetch main page
        html = self.api.get_listings_page()
        if not html:
            print("Failed to fetch listings page")
            return
        
        print(f"HTML Code Length: {len(html)}")
        
        # Parse listings
        listings = self.parser.extract_listings(html)
        print(f"Sections amount: {len(listings)}")
        print()
        
        # Process each listing
        for listing in listings:
            self._enrich_listing(listing)
            listing.display()
            listing.display_to_file("listings.txt")
            listing.display_to_XML("listings.xml")
            self._random_delay()
    
    def _enrich_listing(self, listing: Listing) -> None:
        """Add phone and description to listing"""
        if listing.item_id != "Undefined":
            listing.phone = self.api.get_phone_number(listing.item_id)
            listing.description = self.api.get_item_description(listing.item_id)
    
    def _random_delay(self) -> None:
        """Sleep for a random duration"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)

def main():
    """Main entry point"""
    try:
        token = input("Enter your authorization token: ").strip()
        if not token:
            print("Token cannot be empty")
            return
        
        scraper = KufarScraper(token)
        scraper.scrape()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()