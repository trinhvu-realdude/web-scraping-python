from bs4 import BeautifulSoup
import requests
import csv
import json

BASE_URL = "https://www.mauritius-villa.com"

def get_villa(url: str):
    print(f"Start - Parse the villa ::: {url}")

    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    name = soup.select_one("div.col-sm-8 > h1").text.strip()

    address = ", ".join([
        x.text.strip() for x in soup.select("a.breadcrumb-gtm > span")[::-1]
        if "bedroom" not in x.text and "Home" not in x.text and name not in x.text
    ])

    max_guests = soup.select_one("div.villa-properties > ul.villa-details > li.icon-guests").text[0].strip()

    number_of_bedrooms = soup.select_one("div.villa-properties > ul.villa-details > li.icon-bed").text[0].strip()

    list_of_properties = [li.text.strip() for li in soup.select("div.villa-properties > div.col-xs-8 > ul.weluv > li")]
    
    distances_to = [
        distance.strip() for distance in soup.find("div", class_="legend-nearby").stripped_strings 
        if "-" not in distance and "Distances to" not in distance
    ]

    location_description = soup.select_one("p.villa-description").text.strip()

    services_features = [
        {
            li.select_one("h4").text.replace(":", "").strip(): [
                sub_li.text.replace("\n", "").replace("  ", "").strip() for sub_li in li.select("ul.list-features > li")
            ]
        }
        for li in soup.select("div.row > ul.feature-bloc > li")
    ]

    services_features_dict = {}
    for feature in services_features:
        for key, values in feature.items():
            if key not in services_features_dict:
                services_features_dict[key] = []
            services_features_dict[key].extend(values)

    data = soup.select_one("script:last-child").text.replace("\n", "").replace("  ", "").strip()
    price = data[data.index('"price":') + len('"price":'): data.index(',', data.index('"price":'))]

    print("-> Name:", name)
    print("-> Price per night:", price)
    print("-> Address:", address)
    print("-> Max Guests:", max_guests)
    print("-> Number of Bedrooms:", number_of_bedrooms)
    print("-> Properties:", list_of_properties)
    print("-> Distances To:", distances_to)

    print(f"End - Parse the villa ::: {url}")

    return {
        "Name": name,
        "Price per night": price,
        "Address": address,
        "Max Guests": max_guests,
        "Number of Bedrooms": number_of_bedrooms,
        "Properties": list_of_properties,
        "Distances To": distances_to,
        "Location Description": location_description,
        **services_features_dict
    }


def get_list_of_villas():
    villas = set()

    i = 0
    while i <= 10:
        url = f"{BASE_URL}/en/find?page={i}"

        print(f"Start - Parse page ::: {url}")

        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        for villa in soup.select("div.row > div.villa.col-sm-4.cls_container > div.images > a.main-image"):
            villas.add(f"{BASE_URL}{villa.attrs['href']}")

        i = i + 1

        print(f"End - Parse page ::: {url}")

    return villas

def write_to_csv(data: list):
    json_object = json.dumps(data, indent=4)
    
    with open(f"villa-1.json", "w") as outfile:
        outfile.write(json_object)

    fieldnames = set()  
    for villa in data:
        fieldnames.update(villa.keys())

    with open("villa-1.csv", "w", newline="", encoding="utf-8") as csvfile:
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
    villas = []
    urls = get_list_of_villas()

    for url in urls:
        villa = get_villa(url)
        villas.append(villa)

    write_to_csv(villas)

if __name__ == "__main__":
    parse()


print("Done!")