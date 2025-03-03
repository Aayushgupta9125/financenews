import os
import streamlit as st
from dotenv import load_dotenv
import requests
import google.generativeai as genai
from streamlit_option_menu import option_menu

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

# Function to construct portfolio recommendation prompt
def construct_portfolio_prompt(risk_tolerance, diversification, stocks, assets, duration, investment_amount):
    prompt = f"""
    Act as a professional financial advisor with expertise in portfolio management.
    Provide an optimized investment portfolio recommendation based on:
    - Risk Tolerance: {risk_tolerance}
    - Diversification Preference: {diversification}
    - Preferred Stocks or Sectors: {stocks if stocks else "No specific preference"}
    - Preferred Investment Types (Crypto, ETFs, Real Estate, etc.): {assets if assets else "No specific preference"}
    - Investment Duration: {duration}
    - Total Investment Amount: ₹{investment_amount}

    Your response should include:
    - Suggested asset allocation (stocks, bonds, crypto, etc.)
    - Percentage allocations for each category
    - Expected return estimation for the given risk tolerance
    - Example investment options with potential risk/reward
    - A breakdown of how the investment amount ₹{investment_amount} should be allocated across different asset classes
    - Justification behind each allocation
    """
    return prompt

# Function to generate recommendations
def get_result(input):
    model = gemini_model
    response = model.generate_content(input)
    return response.text

# Main app function
def main():
    st.set_page_config(page_title='Finance Assistant', page_icon='📈', layout='wide')

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
    st.markdown('<p class="title-font">📈 Finance Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtext">Your all-in-one tool for financial news and portfolio recommendations.</p>', unsafe_allow_html=True)
    st.write("")

    # Sidebar Menu
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["📰 Financial News", "📈 Portfolio Finder", "💰 Investment Tips"],
            icons=["newspaper", "graph-up-arrow", "lightbulb"],
        )

    if selected == "📰 Financial News":
        st.subheader("📰 Financial News Hub")
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

    elif selected == "📈 Portfolio Finder":
        st.subheader("📊 Personal Finance Planner")
        st.markdown('<p class="subtext">Get AI-powered investment suggestions based on your risk, preferences, and time horizon.</p>', unsafe_allow_html=True)
        st.write("")

        with st.container():
            col1, col2 = st.columns([1, 1])
            
            risk_tolerance = col1.selectbox(
                'Select Your Risk Tolerance',
                ['Low (Conservative)', 'Medium (Balanced)', 'High (Aggressive)']
            )
            
            diversification = col2.selectbox(
                'Select Your Diversification Preference',
                ['Low (Focused Portfolio)', 'Medium (Balanced)', 'High (Wide Diversification)']
            )

        with st.container():
            col1, col2 = st.columns([1, 1])
            
            stocks = col1.text_area("Enter Preferred Stocks/Sectors (Optional)", placeholder="Example: Tesla, Tech sector, S&P 500")
            
            assets = col2.text_area("Enter Preferred Investment Types (Optional)", placeholder="Example: Crypto, ETFs, Real Estate")

        investment_duration = st.selectbox(
            "Select Your Investment Duration",
            ["Short-term (1-3 years)", "Mid-term (3-7 years)", "Long-term (7+ years)"]
        )

        # New Investment Amount Input
        investment_amount = st.number_input(
            "Enter the Amount You're Ready to Invest (in ₹)", min_value=1000, step=5000, value=50000
        )

        submit = st.button('Get Portfolio Recommendations 🚀')
        
        if submit:
            try:
                portfolio_prompt = construct_portfolio_prompt(risk_tolerance, diversification, stocks, assets, investment_duration, investment_amount)
                result = get_result(portfolio_prompt)
                
                st.subheader("📌 Your AI-Powered Portfolio Recommendations:")
                st.markdown(result, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {str(e)}")

    elif selected == "💰 Investment Tips":
        st.subheader("📜 Essential Investment Tips:")
        st.write("- Diversify across asset classes to reduce risk.")
        st.write("- Invest for the long term rather than short-term speculation.")
        st.write("- Understand your risk tolerance before investing.")
        st.write("- Regularly review and rebalance your portfolio.")
        st.write("- Avoid emotional investing; stick to a strategy.")

if __name__ == '__main__':
    main()