import requests
import xmltodict
import json

from datetime import datetime

from dotenv import load_dotenv
from os import getenv


# https://developer.ieee.org/docs/read/Searching_the_IEEE_Xplore_Metadata_API

# arXiv API
# https://info.arxiv.org/help/api/basics.html


def to_list(obj):
    return obj if isinstance(obj, list) else [obj]


def standardize_arXiv(raw_data):
    doi = raw_data["arxiv:doi"]["#text"]

    # DOI defaults to building the url from scratch (will be updated later on if provided by api)
    links = [{ "type": "doi", "link": f"https://www.doi.org/{doi}" }]

    for link in raw_data["link"]:
        if "@title" in link and link["@title"] == "doi":
            links.pop(0) # remove existing doi
            links.append({ "type": "doi", "link": link["@href"] })
        elif "@title" in link and link["@title"] == "pdf":
            links.append({ "type": "pdf", "link": link["@href"] })
        elif "@type" in link and link["@type"] == "text/html":
            links.append({ "type": "html", "link": link["@href"] })
        else:
            print("WARNING: Unrecognized link \"" + json.dumps(link) + "\"")

    return {
        "doi": doi,
        "title": raw_data["title"],
        "authors": [author["name"] for author in to_list(raw_data["author"])],
        "keywords": [], # TODO: use ChatGPT to generate these
        "summary": raw_data["summary"].replace("\n", " "),
        "published": datetime.fromisoformat(raw_data["published"].rstrip('Z')),
        "links": links
    }

def standardize_springer(raw_data):
    doi = raw_data["doi"]

    # DOI defaults to building the url from scratch (will be updated later on if provided by api)
    links = [{ "type": "doi", "link": f"https://www.doi.org/{doi}" }]

    for link in raw_data["url"]:
        if "doi.org" in link["value"]:
            links.pop(0) # remove existing doi
            links.append({ "type": "doi", "link": link["value"] })
        elif link["format"] == "pdf":
            links.append({ "type": "pdf", "link": link["value"] })
        elif link["format"] == "html":
            links.append({ "type": "html", "link": link["value"] })
        else:
            print("WARNING: Unrecognized link \"" + json.dumps(link) + "\"")

    return {
        "doi": doi,
        "title": raw_data["title"],
        "authors": [creator["creator"] for creator in raw_data["creators"]],
        "keywords": raw_data["keyword"],
        "summary": raw_data["abstract"],
        "published": datetime.strptime(raw_data["publicationDate"], "%Y-%m-%d"),
        "links": links
    }


if __name__ == "__main__":
  load_dotenv()

  arXiv_api_response = requests.get(
      "http://export.arxiv.org/api/query?search_query=all:electron"
  )
  json_arXiv_api_response = xmltodict.parse(arXiv_api_response.text)
  entries = json_arXiv_api_response["feed"]["entry"]
  print(json.dumps(standardize_arXiv(entries[0]), indent=4, default=str))


  # print("---------------------------")

  # springer_api_key = getenv("springer_api_key")
  # springer_api_response = requests.get(
  #     f"https://api.springernature.com/meta/v2/json?api_key={springer_api_key}&q=keyword%3Aelectron&s=1&p=10"
  # )

  # records = springer_api_response.json()["records"]
  # print(json.dumps(standardize_springer(records[0]), indent=4, default=str))


  # ieee_api_key = getenv("ieee_api_key")
  # ieee_api_response = requests.get(f"http://ieeexploreapi.ieee.org/api/v1/search/articles?querytext=electron&format=json&apikey={ieee_api_key}")
