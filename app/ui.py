import streamlit as st

from news_fetcher import fetch_and_store_company_news
from db import get_news_by_company, init_db

init_db()

st.title("Mini News Agent")
st.write("A small demo showcasing company-related news retrival system")

company = st.text_input("Enter Company name: ")

if st.button("Fetch latest news"):
    if not company.strip():
        st.warning("Please enter a company name")
    else:
        with st.spinner("Fetching news..."):
            result = fetch_and_store_company_news(company)
        st.success(f"Fetched {result['fetched']} articles, inserted {result['inserted']} into DB")


if company.strip():
    st.subheader(f"Stored news for {company}")
    news_items = get_news_by_company(company)
    if not news_items:
        st.write("No stored news found for this company")
    else:
        for item in news_items:
            with st.container():
                st.markdown(f"### {item['title']}")
                st.markdown(f"### [Read More]({item['title']})")
                st.markdown(f"### {item['published_at']} | {item['source']}")
                st.markdown(f"---")