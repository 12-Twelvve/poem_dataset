import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from tqdm import tqdm

# Starting URL base (without page number)
base_url = "https://inepal.org/nepalistories/page/"

# CSV file to store poem data
output_file = 'nepali_story.csv'

# File to store the last scraped page number
progress_file = 'scraping_progress_story.txt'

# Batch size to save data after processing a certain number of poems
batch_size = 10

# List to hold the scraped data temporarily
story_data = []

# Function to save data in batches
def save_to_csv(data, file_name):
    df = pd.DataFrame(data)
    if os.path.exists(file_name):
        df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8-sig')  # Append mode
    else:
        df.to_csv(file_name, index=False, encoding='utf-8-sig')

# Function to save the current page number to track progress
def save_progress(page_number, file_name):
    with open(file_name, 'w') as f:
        f.write(str(page_number))

# Function to load the last scraped page number from file
def load_progress(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return int(f.read().strip())
    return 1  # Start from page 1 if no progress file exists

# Load the last scraped page
current_page = load_progress(progress_file)

# Load existing scraped data (to avoid duplicates)
if os.path.exists(output_file):
    existing_data = pd.read_csv(output_file)
    scraped_titles = set(existing_data['Title'])  # Set of already scraped titles to avoid duplicates
else:
    scraped_titles = set()

# Start scraping from the last saved page
while True:
    try:
        print(f"\rScraping page: {current_page}", end='', flush=True)

        # Construct the URL for the current page
        url = base_url + str(current_page)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Find all article elements (assuming each poem is inside an article)
        articles = soup.find_all('article')

        # If no articles found, stop the scraping
        if not articles:
            print("No more poems to scrape. Stopping.")
            break

        # Loop through each article to extract poem info
        # for article in articles:
        for article in tqdm(articles, desc=f"Processing articles on page {current_page}", ncols=80):
        
            try:
                # Extract the title
                title = article.find('h2', class_='entry-title').get_text(strip=True)
                
                # Skip this poem if it's already scraped
                if title in scraped_titles:
                    print(f"Skipping already scraped poem: {title}")
                    continue
                
                # Extract the poem URL and request its content
                story_url = article.find('h2', class_='entry-title').find('a')['href']
                story_response = requests.get(story_url)
                story_soup = BeautifulSoup(story_response.text, 'html.parser')

                # Extract the poem content
                story_content = story_soup.find('div', class_='entry-content').get_text(separator='\n', strip=True)
                
                # Extract the date of publication
                date = story_soup.find('time', class_='entry-date').get_text(strip=True)
                
                # Extract the tags
                # tags =     [tag.get_text(strip=True) for tag in story_soup.find('span', class_='tags-links').find_all('a')]
                
                # Extract the strong line
                strong_line_tag = story_soup.find('strong')
                if strong_line_tag:
                    author_title = strong_line_tag.get_text(strip=True)
                else:
                    author_title = None
                
                # Append the extracted data to the list
                story_data.append({
                    'Title': title,
                    'Author_Title': author_title,
                    'Date': date,
                    'Content': story_content,
                })

                # Update the set of scraped titles
                scraped_titles.add(title)
                
                # Periodically save the data in batches
                if len(story_data) % batch_size == 0:
                    save_to_csv(story_data, output_file)
                    print(f"Saved {len(story_data)} stories..")
                    story_data = []  # Reset the list after saving
            
            # story exception   
            except Exception as e:
                print(f"Error processing Story: {e}")
                continue  # Skip to the next poem if there's an error

        # Save the progress after each page is processed
        save_progress(current_page, progress_file)

        # Move to the next page
        current_page += 1

    # page excception
    except Exception as e:
        print(f"Error processing page {current_page}: {e}")
        continue  # Continue to the next page if there's an error

# Save any remaining poems after the loop ends
if story_data:
    save_to_csv(story_data, output_file)
    print("Final data saved.")
