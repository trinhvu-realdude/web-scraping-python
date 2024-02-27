from bs4 import BeautifulSoup
import requests
import json


URL = "https://www.enjoyalgorithms.com/courses/"
BASE_URL = "https://www.enjoyalgorithms.com"

soup = BeautifulSoup(requests.get(URL).content, "html.parser")

course_list = [
    {
        "course": a.text.replace("Course", "").strip(),
        "url": BASE_URL + a.get("href") 
    }
    for a in soup.select("a.shadow-lg")
]

module_list = []

for course in course_list:
    course_name = course.get("course")
    course_url = course.get("url")
    s = BeautifulSoup(requests.get(course_url).content, "html.parser")

    for div in s.select("div.grid.text-base.tracking-wider > div.bg-white"):
        name = div.select_one("h3.text-base").text.split(".")[1].strip()
        contents = [
            {
                "content": td.text,
                "url": BASE_URL + td.select_one("a").get('href')
            }
            for td in div.select("table.w-full > tbody > tr > td div.text-new-blue")
        ]

        # for content in contents:
        #     url = content["url"]
        #     html_content = str(BeautifulSoup(requests.get(url).content, "html.parser").select_one("div.bg-light-white.pt-5.mx-auto > div.mt-4.tracking-wider"))
        #     content["html"] = html_content

        module = {
            "module": name,
            "contents": contents,
            "course": course
        }

        module_list.append(module)


json_object = json.dumps(module_list, indent=4)
 
with open("result.json", "w") as outfile:
    outfile.write(json_object)