from bs4 import BeautifulSoup
import requests
import csv
import json
from bs4 import Tag

BASE_URL = "https://www.villanovo.com"

def get_villa(url: str):
    print(f"Start - Parse the villa ::: {url}")

    try:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        name = soup.select_one("div.villa-infos-header > h1:first-child").text.strip()

        address = ", ".join([
            item.text.replace("»", "").strip()
            for item in soup.select("div.bread-crumbs:first-child > div")[::-1]
            if "Home" not in item.text and "Villa rentals" not in item.text and name not in item.text
        ])

        max_guests = [
            span.text.strip() 
            for span in soup.select("label.occupancies > span") 
            if "traveler" in span.select_one("img").attrs["src"]
        ][0]
        
        number_of_bedrooms = [
            span.text.strip() 
            for span in soup.select("label.occupancies > span") 
            if "bed" in span.select_one("img").attrs["src"]
        ][0]

        number_of_bathrooms = [
            span.text.strip() 
            for span in soup.select("label.occupancies > span") 
            if "bath" in span.select_one("img").attrs["src"]
        ][0]

        description = soup.select_one("div.villa-infos > p").text.strip()
        
        services = [
            {
                p.text: [
                    str(li).replace("<li>", "").replace("</li>", "").strip()
                    for li in p.next_sibling if str(li) != "<br/>"
                ]
            }
            for p in soup.select("div.expandable-zone > p.ph, div.villa-nav-content > p.ph") if type(p.next_sibling) is Tag
        ]
        services_dict = {}
        for feature in services:
            for key, values in feature.items():
                if key not in services_dict:
                    services_dict[key] = []
                services_dict[key].extend(values)

        prices = [
            "".join([c for c in td.text.strip() if c.isdigit()])
            for td in soup.select("table.table-prices td.text-right")
        ]

        if len(prices) > 0:
            min_price = min(prices)
            max_price = max(prices)
        else:
            min_price = "".join([c for c in soup.select_one("div.from-price").text.strip() if c.isdigit()])
            max_price = min_price

        return {
            "Name": name,
            "Address": address,
            "Max guests": max_guests,
            "Number of bedrooms": number_of_bedrooms,
            "Number of bathrooms": number_of_bathrooms,
            "Description": description,
            "Min price": min_price,
            "Max price": max_price,
            **services_dict
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    

    print(f"End - Parse the villa ::: {url}")

def get_villas_by_city(city: str):
    villas = set()
    page = 1

    print(f"Start - Parse the city ::: {city}")

    while True:
        url = city + f"?page={page}"

        print(f"-> Checking page {page} ::: {url}")

        try: 
            soup = BeautifulSoup(requests.get(url).content, "html.parser")

            if "Page not found" in soup.text: 
                print(f"Page not found for URL {url}")
                break

            urls = [
                BASE_URL + item.attrs["href"] 
                for item in soup.select(
                    "div.row.villas > div.is-sort > div.villa > div.villa-img > a:first-child"
                )
            ]
            villas.update(urls)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")

        page = page + 1

    print(f"Found {len(villas)} villas")

    print(f"End - Parse the city ::: {city}")

    return villas

def write_to_csv(data: list):
    json_object = json.dumps(data, indent=4)
    
    with open(f"villa-2.json", "w") as outfile:
        outfile.write(json_object)

    fieldnames = set()  
    for villa in data:
        fieldnames.update(villa.keys())

    with open("villa-2.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for villa in data:
            for key, values in villa.items():
                if isinstance(values, list):
                    villa[key] = "\n- ".join(values)
                    if not villa[key].startswith("\n- "):
                        villa[key] = "\n- " + villa[key]

            writer.writerow(villa)

def parse():
    soup = BeautifulSoup(requests.get(BASE_URL).content, "html.parser")

    cities = [BASE_URL + city.attrs["href"] for city in soup.select("div.cities > a")]

    list_of_villas = set()

    for city in cities:
        villas = get_villas_by_city(city)
        list_of_villas.update(villas)

    result = []
    for url in list_of_villas:
        villa = get_villa(url)
        result.append(villa)

    write_to_csv(result)

if __name__ == "__main__":
    parse()
    # test = get_villa("https://www.villanovo.com/villa-rentals/europe/spain/costa-brava/aigua-blava/villa-blanc")
    # test = get_villa("https://www.villanovo.com/villa-rentals/africa/morocco/marrakech/marrakech-medina/dar-118")

print("Done!")