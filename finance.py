import os
import streamlit as st
from dotenv import load_dotenv
import requests
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash-001')

# Function to fetch financial news
def fetch_financial_news(company_name):
    news_api_key = os.getenv("NEWS_API_KEY")  # Replace with your actual NewsAPI key
    url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={news_api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            if not articles:
                return None  # No articles found
            return articles
        else:
            print(f"Error: Unable to fetch news. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None

# Function to summarize articles using Gemini
def summarize_articles(articles):
    summaries = []
    for article in articles[:5]:  # Summarize top 5 articles
        prompt = f"""
        Summarize the following article in 2-3 sentences:
        Title: {article['title']}
        Description: {article['description']}
        Content: {article['content']}
        """
        try:
            response = gemini_model.generate_content(prompt)
            summary = response.text.strip()
            summaries.append(summary)
        except Exception as e:
            print(f"Error generating summary: {e}")
            summaries.append("Unable to generate summary.")
    return summaries

# Main app function
def main():
    st.set_page_config(page_title='Financial News App', page_icon='📰', layout='wide')

    # Custom Styling
    st.markdown(
        """
        <style>
        .title-font {
            font-size:36px !important;
            font-weight: bold;
            color: #2E86C1;
            text-align: center;
        }
        .subtext {
            font-size:18px !important;
            color: #555;
            text-align: center;
        }
        .stButton>button {
            background-color: #2E86C1;
            color: white;
            font-size: 16px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # App Title
    st.markdown('<p class="title-font">📰 Financial News Hub</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtext">Stay updated with the latest financial news about your favorite companies.</p>', unsafe_allow_html=True)
    st.write("")

    # Input for company name
    company_name = st.text_input("Enter the name of the company:", placeholder="Example: Tesla, Apple, Microsoft")

    if st.button("Fetch and Summarize News 📰"):
        if company_name.strip() == "":
            st.warning("Please enter a valid company name.")
        else:
            with st.spinner("Fetching news..."):
                articles = fetch_financial_news(company_name)

            if articles:
                st.success(f"Found {len(articles)} articles related to '{company_name}'.")
                summaries = summarize_articles(articles)

                st.subheader("Summarized News Articles:")
                for i, summary in enumerate(summaries):
                    st.markdown(f"""
                    #### Article {i+1}
                    {summary}
                    """)
            elif articles is None:
                st.error("No news articles found. Please try again later or check your API key.")
            else:
                st.error("An error occurred while fetching news. Please try again later.")

if __name__ == '__main__':
    main()