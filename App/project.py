import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager as ChromeDriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_wikipedia_data(url, scrape_headlines, selected_headlines_tags, scrape_links):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriver().install()), options=options)

    try:
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        tables = soup.find_all("table", {"class": "wikitable"})
        all_table_data = []
        if tables:
            for i, table in enumerate(tables, 1):
                st.write(f"Scraping Table {i}...")
                rows = table.find_all("tr")
                headers = [th.text.strip() for th in rows[0].find_all("th")]

                data = []
                for row in rows[1:]:
                    cols = row.find_all(["th", "td"])
                    cols = [col.text.strip() for col in cols]
                    
                    while len(cols) < len(headers):
                        cols.append("")  
                    if len(cols) > len(headers):
                        cols = cols[:len(headers)]  
                    data.append(cols)

                df = pd.DataFrame(data, columns=headers)
                all_table_data.append(df)
        else:
            st.warning("No tables found on this page.")

        headlines = []
        if scrape_headlines:
            if selected_headlines_tags:
                for tag in selected_headlines_tags:
                    headline_tags = soup.find_all(tag)
                    headlines += [tag.text.strip() for tag in headline_tags]

        links = []
        if scrape_links:
            anchor_tags = soup.find_all("a", href=True)
            links = [a['href'] for a in anchor_tags if a['href'].startswith("http")]

        return all_table_data, headlines, links, soup, None

    except Exception as e:
        return None, None, None, f"Error occurred: {str(e)}"

def start_scraping(url, scrape_headlines, selected_headlines_tags, scrape_links, scrape_images_flag=False):
    with st.spinner("Scraping in progress..."):
        table_data, headlines, links, soup, error = scrape_wikipedia_data(url, scrape_headlines, selected_headlines_tags, scrape_links)
        if error:
            st.error(error)
        else:
            st.success("Data scraped successfully!")

            for i, df in enumerate(table_data, 1):
                st.write(f"Table {i}:")
                st.write(df)
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"Download Table {i} CSV",
                    data=csv,
                    file_name=f"table_{i}.csv",
                    mime="text/csv",
                )

            if headlines:
                st.write("Headlines Found:")
                for headline in headlines:
                    st.write(f"- {headline}")

            if links:
                st.write("Links Found:")
                for link in links:
                    st.write(f"- {link}")

                links_df = pd.DataFrame(links, columns=["Links"])
                
                csv_links = links_df.to_csv(index=False)
                 
                st.download_button(
                    label="Download Links CSV", 
                    data=csv_links,
                    file_name="scraped_links.csv",
                    mime="text/csv",
                )

st.title("WEB SCRAPER")
st.write("Table, Headline, and Link Scraper")

# Add custom CSS for background gradient color
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #f0f0f0, #d3d3d3);
    }
    .about-section {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# About section
st.markdown(
    """
    <div class="about-section">
        <h2>About Web Scraping</h2>
        <p>Web scraping is an automated method used to extract large amounts of data from websites quickly and efficiently. 
        It involves fetching the content of web pages and parsing the data to retrieve the desired information. 
        This technique is widely used for data analysis, research, and various other applications where data from the web is required.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar for input and button
st.sidebar.title("Scraping Options")
url = st.sidebar.text_input("Enter the URL:")
scrape_headlines = st.sidebar.checkbox("Scrape Headlines")
headline_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
selected_headlines_tags = st.sidebar.multiselect("Select headlines to scrape:", headline_tags)
scrape_links = st.sidebar.checkbox("Scrape Links")

if st.sidebar.button("Start Scraping"):
    start_scraping(url, scrape_headlines, selected_headlines_tags, scrape_links)
    st.sidebar.write("Enter a URL to start scraping data from Wikipedia. You can choose to scrape tables, headlines, and links from the page.")
    st.sidebar.write("Example URL: https://en.wikipedia.org/wiki/Web_scraping")
    def scrape_images(soup):
        images = []
        img_tags = soup.find_all("img")
        for img in img_tags:
            img_url = img.get("src")
            if img_url and img_url.startswith("http"):
                images.append(img_url)
        return images

    # Add image scraping to the start_scraping function
    def start_scraping(url, scrape_headlines, selected_headlines_tags, scrape_links, scrape_images_flag=False):
        with st.spinner("Scraping in progress..."):
            table_data, headlines, links, soup, error = scrape_wikipedia_data(url, scrape_headlines, selected_headlines_tags, scrape_links)
            if error:
                st.error(error)
            else:
                st.success("Data scraped successfully!")

                for i, df in enumerate(table_data, 1):
                    st.write(f"Table {i}:")
                    st.write(df)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"Download Table {i} CSV",
                        data=csv,
                        file_name=f"table_{i}.csv",
                        mime="text/csv",
                    )

                if headlines:
                    st.write("Headlines Found:")
                    for headline in headlines:
                        st.write(f"- {headline}")

                if links:
                    st.write("Links Found:")
                    for link in links:
                        st.write(f"- {link}")

                    links_df = pd.DataFrame(links, columns=["Links"])
                    
                    csv_links = links_df.to_csv(index=False)
                     
                    st.download_button(
                        label="Download Links CSV", 
                        data=csv_links,
                        file_name="scraped_links.csv",
                        mime="text/csv",
                    )

                # Scrape and display images
                if scrape_images_flag:
                    images = scrape_images(soup)
                    if images:
                        st.write("Images Found:")
                        for img_url in images:
                            st.image(img_url)
                            st.write(img_url)
                if images:
                    st.write("Images Found:")
                    for img_url in images:
                        st.image(img_url)
                        st.write(img_url)