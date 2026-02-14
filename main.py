import requests
from requests.exceptions import ReadTimeout
from bs4 import BeautifulSoup
import traceback

r = requests.get('https://www.kufar.by/l')
r.encoding = "utf-8"
html_code = r.text
print("HTML Code Length: " + str(len(html_code)))

soup = BeautifulSoup(html_code, "html.parser")

#with open("output.html", "w", encoding="utf-8") as file:
#    file.write(soup.prettify())

print(soup.title.string)

sections = soup.find_all("section")
print("Sections amount: " + str(len(sections)))
print()

for section in sections:
    h3_title = section.find("h3")
    if h3_title == None:
        continue # This isn't a section we need
    
    spans = section.find_all("span")
    price_text = "Undefined"
    date_text = "Undefined"
    for span in spans:
        if "styles_price" in str(span.parent.get("class")):
            price_text = str(span.text)
    
    p_elems = section.find_all("p")
    region_text = "Undefined"
    for p_elem in p_elems:
        if "styles_region" in str(p_elem.get("class")):
            region_text = str(p_elem.text)
    
    a_elem = section.find("a")
    link_url = a_elem.get("href")
    link_url = link_url.split("/")[-1]
    item_id = link_url.split("?")[0]

    phone_text = "Undefined"
    try:
        phone_req = requests.get(f"https://api.kufar.by/search-api/v2/item/{item_id}/phone")
        
        phone_req_json = phone_req.json()
        
        if phone_req_json.get("error") != None:
            phone_text = "Error"
            error_dict = phone_req_json.get("error")
            if not isinstance(error_dict, str):    
                if error_dict.get("message") != None:
                    phone_text += ": " + error_dict.get("message")
        else:
            phone_text = phone_req_json.get("phone")
            if phone_text == None:
                phone_text = "Undefined"
    except ReadTimeout: 
        phone_text = "Timeout"
    
    description_text = "Undefined"
    try:
        description_req = requests.get(f"https://www.kufar.by/item/{item_id}")
        description_req.encoding = "utf-8"
        description_text = ""
        desc_html_code = description_req.text
        desc_soup = BeautifulSoup(desc_html_code, "html.parser")
        desc_divs = desc_soup.find_all("div")
        for desc_div in desc_divs:
            # Parameters block
            if desc_div.get("data-name") and "parameters-block" in desc_div.get("data-name"):
                h2_elem = desc_div.find("h2")
                description_text += str(h2_elem.text) + "\n"
                param_div_sections = desc_div.find_all("div")
                for param_div in param_div_sections:
                    if "styles_parameter_label" in str(param_div.get("class")):
                        description_text += str(param_div.text) + " "
                    if "styles_parameter_value" in str(param_div.get("class")):
                        description_text += str(param_div.text) + "\n"
            # Description label
            if desc_div.get("itemprop") == "description":
                desc_text_code = str(desc_div.prettify())
                desc_text_code = desc_text_code.replace('<div itemprop="description">', "")
                desc_text_code = desc_text_code.replace('</div>', "")
                desc_text_code = desc_text_code.replace('<br/>', "\n")
                desc_text_code = desc_text_code.rstrip()
                description_text += desc_text_code
    except Exception as ex:
        print("Exception occurred")
        print(ex)
        print("Here's a traceback for you, big boy...")
        traceback.print_exc()

    print("Title: " + str(h3_title.text))
    print("Price: " + price_text)
    print("Region: " + region_text)
    print("ID: " + item_id)
    print("Phone: " + phone_text)
    print("Description: " + description_text)

    print("-" * 30)
    print()
    print()
    print()