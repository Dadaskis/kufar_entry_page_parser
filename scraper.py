import time
import random
from api import KufarAPI
from parser import ListingParser

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
    
    def _enrich_listing(self, listing) -> None:
        """Add phone and description to listing"""
        if listing.item_id != "Undefined":
            listing.phone = self.api.get_phone_number(listing.item_id)
            listing.description = self.api.get_item_description(listing.item_id)
    
    def _random_delay(self) -> None:
        """Sleep for a random duration"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)