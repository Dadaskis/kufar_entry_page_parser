from bs4 import BeautifulSoup
from typing import Optional, List
from listing import Listing

class ListingParser:
    """Parses listings from HTML"""
    
    @staticmethod
    def extract_listings(html: str) -> List[Listing]:
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