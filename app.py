import streamlit as st
import requests
import PyPDF2
from bs4 import BeautifulSoup


GROQ_API_KEY = st.secrets["general"]["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def extract_text_from_pdf(pdf_file):
    """Extract text from an uploaded PDF file."""
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def scrape_university_page(url):
    """Scrape text content from a university webpage."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    return "Error: Unable to fetch webpage."

def query_groq_api(prompt):
    """Query the Groq LLM API with the given prompt."""
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(GROQ_API_URL, json=data, headers=headers)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response.")

def main():
    st.title("PDF & Web Scraper Chatbot")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    
    # URL Input
    website_url = st.text_input("Enter university webpage URL")
    
    # User Query Input
    user_query = st.text_area("Enter your query")
    
    if st.button("Get Answer"):
        context = ""
        
        if uploaded_file:
            context += extract_text_from_pdf(uploaded_file)[:4000]  # Limit to avoid large inputs
        
        if website_url:
            context += scrape_university_page(website_url)[:4000]
        
        if user_query:
            prompt = f"Context: {context}\nUser Query: {user_query}"
            response = query_groq_api(prompt)
            st.write("### Response:")
            st.write(response)
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()
