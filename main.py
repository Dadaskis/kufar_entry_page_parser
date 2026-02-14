import requests
from requests.exceptions import ReadTimeout
from bs4 import BeautifulSoup
import traceback
import time
import random

token = input("Enter your authorization token: ")

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
user_agent_headers_simple = {
    "User-Agent" : user_agent,
}
user_agent_headers = {
    "User-Agent" : user_agent,
    "Origin" : "https://www.kufar.by",
    "Referer" : "https://www.kufar.by/",
    "Priority" : "u=4",
    "Host" : "api.kufar.by",
    "Accept" : "*/*",
    "Accept-Language" : "en-US,en;q=0.9",
    "Accept-Encoding" : "gzip, deflate, br, zstd",
    "Content-type" : "application/json",
    "g-recaptcha-response" : "",
    "X-App-Name" : "Web Kufar",
    "X-Pulse-Environment-Id" : "6bc55ac4-4edd-4d5e-8f24-f188ac377de7",
    "X-Rudder-Anonymous-Id" : "6bc55ac4-4edd-4d5e-8f24-f188ac377de7",
    "X-App-Request-Source" : "ad_view",
    "Connection" : "keep-alive",
    "Sec-Fetch-Dest" : "empty",
    "Sec-Fetch-Mode" : "cors",
    "Sec-Fetch-Site" : "same-site",
    "TE": "trailers"
}
phone_token_headers = {
    "User-Agent" : user_agent,
    "Authorization" : token,
    "Origin" : "https://www.kufar.by",
    "Referer" : "https://www.kufar.by/",
    "Priority" : "u=4",
    "Host" : "api.kufar.by",
    "Accept" : "*/*",
    "Accept-Language" : "en-US,en;q=0.9",
    "Accept-Encoding" : "gzip, deflate, br, zstd",
    "Content-type" : "application/json",
    "g-recaptcha-response" : "",
    "X-App-Name" : "Web Kufar",
    "X-Pulse-Environment-Id" : "6bc55ac4-4edd-4d5e-8f24-f188ac377de7",
    "X-Rudder-Anonymous-Id" : "6bc55ac4-4edd-4d5e-8f24-f188ac377de7",
    "X-App-Request-Source" : "ad_view",
    "Connection" : "keep-alive",
    "Sec-Fetch-Dest" : "empty",
    "Sec-Fetch-Mode" : "cors",
    "Sec-Fetch-Site" : "same-site",
    "TE": "trailers"
}

r = requests.get('https://www.kufar.by/l', headers=user_agent_headers_simple)
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
        phone_req = requests.get(f"https://api.kufar.by/search-api/v2/item/{item_id}/phone", headers=phone_token_headers)
        phone_options_req = requests.options(f"https://api.kufar.by/search-api/v2/item/{item_id}/phone", headers=user_agent_headers)
        stat_ping_req = requests.put(f"https://statpoints.kufar.by/v1/statpoints/increment?ad={item_id}&statpoint=phoneview", headers=user_agent_headers)
        cre_post_req = requests.post(
            f"https://cre-api.kufar.by/fb-event-broker/v1/event",
            headers=phone_token_headers,
            data={
                "event_name" : "Generalist_call_click",
                "event_id" : "7535499026424987",
                "action_source" : "website",
                "event_source_url" : f"https://www.kufar.by/item/{item_id}?searchId=4e6e01c4-ef44-462e-b1f0-eda88e65fc5d&r_block=Previously%20Viewed"
            }
        )
        stat_ping_options_req = requests.put(f"https://statpoints.kufar.by/v1/statpoints/increment?ad={item_id}&statpoint=phoneview", headers=user_agent_headers)
        cre_post_options_req = requests.post(f"https://cre-api.kufar.by/fb-event-broker/v1/event", headers=user_agent_headers)

        phone_req_json = phone_req.json()
        
        if phone_req_json.get("error") != None:
            phone_text = "Error"
            error_dict = phone_req_json.get("error")
            if not isinstance(error_dict, str):    
                if error_dict.get("message") != None:
                    phone_text += ": " + error_dict.get("message")
            else:
                phone_text += ": " + str(error_dict)
        else:
            phone_text = phone_req_json.get("phone")
            if phone_text == None:
                phone_text = "Undefined"
    except ReadTimeout: 
        phone_text = "Timeout"
    
    description_text = "Undefined"
    try:
        description_req = requests.get(f"https://www.kufar.by/item/{item_id}", headers=user_agent_headers_simple)
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

    time.sleep(random.uniform(10, 20))