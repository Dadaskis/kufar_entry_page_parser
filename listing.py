from dataclasses import dataclass
import os
from datetime import datetime
from lxml import etree

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