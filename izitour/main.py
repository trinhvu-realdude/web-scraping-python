from bs4 import BeautifulSoup, Tag
import requests as req
import json

EXCURSION_URL = "https://izitour.com/en/vietnam-tour"
PACKAGE_TOUR_URL = "https://izitour.com/en/vietnam-package-tours"
CAR_RENTAL_URL = "https://izitour.com/en/vietnam-car-rental"

EXCURSION = "excursion"
PACKAGE_TOUR = "package-tour"
CAR_RENTAL = "car-rental"

def get_tour(ul: Tag):
    title = ul.select_one("li.title14").text.strip()
    duration = ul.select_one("li.duration").text.split(":")[1].strip()
    start_end = ul.select_one("li.startend").text.split(":")[1].strip()
    visit = ul.select_one("li.visit").text.split(":")[1].strip()
    category = ul.select_one("li.person").text.split(":")[1].strip()
    tour_guide_in = ul.select_one("li.micro").text.split(":")[1].strip()
    travel_style = ul.select_one("li.wishes").text.split(":")[1].strip()
    price = {
        "USD": int(ul.select_one("li.boxprice").text.split("(")[0].replace("From", "").replace("$", "").replace(",", "").strip()),
        "VND": int(ul.select_one("li.boxprice").text.split("(")[1].replace(")", "").replace("VND", "").replace(",", "").strip())
    }

    tour = {
        "title": title,
        "duration": duration,
        "start_end": start_end,
        "visit": visit,
        "category": category,
        "tour_guide_in": tour_guide_in,
        "travel_style": travel_style,
        "price": price
    }

    print(f"Saved tour {title}")

    return tour

def get_list_of_tours(filename: str, endpoint: str, number_of_tours: int):

    print(f"Parsing {filename}")

    page = 1

    list_of_tours = []

    while len(list_of_tours) != number_of_tours: 
        URL = f"https://izitour.com/en/{page}/12/{endpoint}"
        print(f"Fetching page {page} of {URL}")
        s = BeautifulSoup(req.get(URL).content, "html.parser")

        for ul in s.select("ul.uk-list.itemtour"):
            tour = get_tour(ul)
            list_of_tours.append(tour)

        page = page + 1

    result = {
        "length": len(list_of_tours),
        "data": list_of_tours
    }

    json_object = json.dumps(result, indent=4)
    
    with open(f"{filename}.json", "w") as outfile:
        outfile.write(json_object)

    print(f"Done {filename}")



def parse(url: str, type: str):
    soup = BeautifulSoup(req.get(url).content, "html.parser")

    match type:
        case "excursion":
            number_of_tours = int(soup.select_one("div.uk-container-center > div.uk-text-right.shortduration > span.price").text)
            get_list_of_tours(type, "vietnam-tour", number_of_tours)

        case "package-tour":
            number_of_tours = int(soup.select_one("div.uk-container-center > div.uk-text-right.shortduration > span.price").text)
            get_list_of_tours(type, "vietnam-package-tours", number_of_tours)

        case "car-rental":
            get_list_of_tours(type, "vietnam-car-rental", number_of_tours=98)

if __name__ == "__main__":
    parse(EXCURSION_URL, EXCURSION)
    parse(PACKAGE_TOUR_URL, PACKAGE_TOUR)
    parse(CAR_RENTAL_URL, CAR_RENTAL)

print("Done!")

