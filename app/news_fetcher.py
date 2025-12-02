import requests
import json
import sys

API_KEY="d7f2107e29d84d7792e75ed266afbb2c"
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_news_raw(comapny_name:str):
    params={
        "q":comapny_name,
        "language":'en',
        "sortBy":"publishedAt",
        "pageSize":10,
        "apikey":API_KEY
    }
    response = requests.get(BASE_URL,params=params)
    response.raise_for_status()
    data = response.json()
    return data

def extract_news_items(data:dict, company_name: str):
    articles = data.get("articles",[])
    cleaned =[]

    for article in articles:
        title = article.get("title") or ""
        url = article.get("url") or ""
        published_at = article.get("publishedAt") or ""
        source_name = article.get("source" or {}).get("name") or ""

        if company_name.lower() in title.lower():
            cleaned.append(
                {
                    "company": company_name,
                    "title": title.strip(),
                    "url": url.strip(),
                    "published_at": published_at,
                    "source": source_name.strip(),
                }
            )

    return cleaned

def fetch_and_store_company_news(company:str)->dict:
    company = company.strip()

    from db import init_db, insert_news_items

    init_db()
    data = fetch_news_raw(company)
    items = extract_news_items(data, company)
    inserted = insert_news_items(company, items)

    return{
        "company":company,
        "fetched":len(items),
        "inserted":inserted,
        "items":items
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.news_fetcher <company_name>")
        sys.exit(1)
    
    company = "".join(sys.argv[1:]).strip()
    result = fetch_and_store_company_news(company)

    if result["fetched"] == 0:
        print(f"No news found matching {company}")
        sys.exit(0)
    
    print(f"Fetched {result['fetched']} items, inserted {result['inserted']} new rows into DB. \n")

    print(f"News for '{company}':")
    print("-" * 40)
    for item in result["items"]:
        print(f"- {item['title']}")
        print(f"  {item['url']}")
        print(f"  ({item['published_at']} | {item['source']})")
        print()