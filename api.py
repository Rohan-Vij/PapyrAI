import requests
import xmltodict
import json

from datetime import datetime

from dotenv import load_dotenv
from os import getenv

load_dotenv()


# https://developer.ieee.org/docs/read/Searching_the_IEEE_Xplore_Metadata_API

# arXiv API
# https://info.arxiv.org/help/api/basics.html


def to_list(obj):
    return obj if isinstance(obj, list) else [obj]


def standardize_arXiv(raw_data):
    # TODO: links

    doi = raw_data["arxiv:doi"]["#text"]        

    return {
        "doi": doi,
        "title": raw_data["title"],
        "authors": [author["name"] for author in to_list(raw_data["author"])],
        "keywords": [], # TODO: use ChatGPT to generate these
        "summary": raw_data["summary"],
        "published": datetime.fromisoformat(raw_data["published"]),
        "link": f"https://www.doi.org/{doi}"
    }

def standardize_springer(raw_data):
    # TODO: links

    doi = raw_data["doi"]

    return {
        "doi": doi,
        "title": raw_data["title"],
        "authors": [creator["creator"] for creator in raw_data["creators"]],
        "keywords": raw_data["keyword"],
        "summary": raw_data["abstract"],
        "published": datetime.strptime(raw_data["publicationDate"], "%Y-%m-%d"),
        "link": f"https://www.doi.org/{doi}"
    }


arXiv_api_response = requests.get(
    "http://export.arxiv.org/api/query?search_query=all:electron"
)
json_arXiv_api_response = xmltodict.parse(arXiv_api_response.text)
entries = json_arXiv_api_response["feed"]["entry"]
print(json.dumps(standardize_arXiv(entries[0]), indent=4, default=str))


print("---------------------------")

springer_api_key = getenv("springer_api_key")
springer_api_response = requests.get(
    f"https://api.springernature.com/meta/v2/json?api_key={springer_api_key}&q=keyword%3Aelectron&s=1&p=10"
)

records = springer_api_response.json()["records"]
print(json.dumps(standardize_springer(records[0]), indent=4, default=str))


# ieee_api_key = getenv("ieee_api_key")
# ieee_api_response = requests.get(f"http://ieeexploreapi.ieee.org/api/v1/search/articles?querytext=electron&format=json&apikey={ieee_api_key}")
