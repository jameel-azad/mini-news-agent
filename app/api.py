from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

from news_fetcher import fetch_and_store_company_news
from db import get_news_by_company, init_db

app = FastAPI(title="Mini News Agent")

class FetchNewsRequest(BaseModel):
    company: str

class NewsItem(BaseModel):
    company: str
    title: str
    url: str
    published_at: Optional[str] = None
    source: Optional[str] = None

@app.post("/fetch-news")
def fetch_news(req: FetchNewsRequest):
    result = fetch_and_store_company_news(req.company)
    return {
        "company": result["company"],
        "fetched": result["fetched"],
        "inserted": result["inserted"],
        "items": result["items"]
    }

@app.get("/news", response_model=List[NewsItem])
def get_news(company: str = Query(...,description="Company name"), limit: int = 10):
    init_db()
    rows = get_news_by_company(company, limit=limit)
    return rows