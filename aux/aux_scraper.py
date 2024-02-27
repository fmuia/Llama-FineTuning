# utils.py
import re
import csv
import time
import math
import pandas as pd
import unicodedata
from collections import Counter

import arxiv

import matplotlib.pyplot as plt
import seaborn as sns


from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Useful functions

def prepare_base_url(full_url):
    parsed_url = urlparse(full_url)
    query_params = parse_qs(parsed_url.query)
    query_params.pop('page', None)

    # Reconstruct the query string, ensuring spaces are encoded correctly
    query_string = "&".join(f"{key}={value[0].replace(' ', '%20')}" for key, value in query_params.items())
    new_parsed_url = parsed_url._replace(query=query_string)
    
    return urlunparse(new_parsed_url)

def get_total_pages_from_inspire(driver, full_query_url):
    # Prepare the base URL by removing the 'page' parameter
    base_url = prepare_base_url(full_query_url)
    print(base_url)
    
    # Fetch the first page to get the total number of results
    driver.get(base_url + "&page=1")
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for the page to load
    time.sleep(2)  # Adjust this time based on your network speed

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the total number of results
    results_span = soup.find('span', string=re.compile(r'\d+\sresults'))
    total_results = int(results_span.text.split()[0].replace(',', '')) if results_span else 0
    
    # Extract the results per page from the URL
    match = re.search(r"&size=(\d+)&", full_query_url)
    results_per_page = int(match.group(1)) if match else 25  # Default to 25 if not found
    
    # Calculate the total number of pages
    total_pages = math.ceil(total_results / results_per_page)
    
    return total_pages

# Function to extract the number of papers per page
def get_papers_per_page(url):
    # Regular expression to find the size parameter
    match = re.search(r"&size=(\d+)&", url)

    return int(match.group(1))

# Function to extract DOI
def extract_doi(entry):
    doi_pattern = re.compile(r'(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)')
    doi = None
    doi_tag = entry.find('a', href=doi_pattern)
    if doi_tag:
        doi_match = doi_pattern.search(doi_tag['href'])
        doi = doi_match.group(0) if doi_match else None
    return doi

# Function to extract ePrint number
def extract_eprint_number(entry):
    eprint_number = None
    eprint_section = entry.find(lambda tag: tag.name == 'a' and 'arxiv.org' in tag.get('href', ''))
    if eprint_section:
        eprint_number = eprint_section.get_text(strip=True)
    return eprint_number

# Function to extract arXiv category
def extract_arxiv_category_v2(entry):
    arxiv_category = None
    eprint_link = entry.find(lambda tag: tag.name == 'a' and 'arxiv.org' in tag.get('href', ''))
    if eprint_link:
        category_span = eprint_link.find_next_sibling('span')
        if category_span:
            arxiv_category = category_span.get_text(strip=True).strip('[]')
    return arxiv_category

# Revised function to extract citation counts based on the demonstrated algorithm
def extract_citation_count_v2(entry):
    citation_tag = entry.find_next(lambda tag: tag.name == 'span' and ('citation' in tag.text or 'citations' in tag.text))
    if citation_tag:
        # Remove commas from the string before converting to int
        citation_count = int(citation_tag.text.split()[0].replace(',', ''))
        return citation_count
    return 0

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.decode('ASCII')

def standardize_author_name(name):
    """
    Standardize author name by adding spaces between concatenated initials (if present)
    and then abbreviating the first name (if not already an initial) and keeping the rest of the name as is.

    Args:
    name (str): The author's full name.

    Returns:
    str: Standardized author name.
    """
    parts = name.split()
    if not parts:
        return ""

    # Add spaces between concatenated initials in the first part of the name
    if '.' in parts[0] and parts[0][-1] == '.':
        initials = [char + '.' for char in parts[0] if char != '.']
        parts[0] = ' '.join(initials)

    # If the first part is already an initial, leave it as is
    if parts[0].endswith('.'):
        return ' '.join(parts)

    # Otherwise, transform the first word into an initial and keep the rest as is
    standardized_name = parts[0][0] + '. ' + ' '.join(parts[1:])
    return standardized_name

def extract_authors(entry):
    authors_tags = entry.find_all('a', {'data-test-id': 'author-link'})
    authors_list = [standardize_author_name(remove_accents(tag.get_text(strip=True))) for tag in authors_tags]
    return ", ".join(authors_list)


# Function to filter out duplicate and invalid entries
def filter_valid_entries(entries):
    filtered_entries = []
    seen_titles = set()
    for entry in entries:
        title = entry.find('span', {'data-test-id': 'literature-detail-title'})
        authors = entry.find_all('a', {'data-test-id': 'author-link'})
        if title and authors and title.get_text(strip=True) not in seen_titles:
            seen_titles.add(title.get_text(strip=True))
            filtered_entries.append(entry)
    return filtered_entries

def fetch_abstract(eprint_number):
    if not eprint_number:
        return "Abstract not found"
    try:
        client = arxiv.Client()
        search = arxiv.Search(id_list=[eprint_number])
        for result in client.results(search):
            abstract = result.summary.replace('\n', ' ')
            return abstract
    except Exception as e:
        return f"Error fetching abstract: {str(e)}"
    return "Abstract not found"

def extract_title_with_latex(entry):
    title_element = entry.find('span', {'data-test-id': 'literature-detail-title'})
    if not title_element:
        return None

    def extract_text_latex(el):
        text_parts = []
        for content in el.children:
            if isinstance(content, NavigableString):
                current_text = str(content)
                if text_parts:
                    # Check and adjust space at the interface
                    if text_parts[-1].endswith(" ") and current_text.startswith(" "):
                        current_text = current_text.lstrip()  # Remove leading space
                    elif not text_parts[-1].endswith(" ") and not current_text.startswith(" "):
                        current_text = " " + current_text  # Add leading space
                text_parts.append(current_text)
            elif content.name == 'span' and 'katex' in content.get('class', []):
                # Extract LaTeX content
                latex_annotation = content.find('annotation', encoding='application/x-tex')
                if latex_annotation:
                    latex_text = latex_annotation.get_text()
                    # Check and adjust space at the interface
                    if text_parts and not text_parts[-1].endswith(" "):
                        latex_text = " " + latex_text
                    if not latex_text.endswith(" "):
                        latex_text += " "
                    text_parts.append(latex_text)
            elif content.name:
                # Recursively process other elements
                text_parts.append(extract_text_latex(content))
        return ''.join(text_parts)

    return extract_text_latex(title_element)

def scrape_page_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all entries on the page
    entries = soup.find_all(lambda tag: tag.name == 'div' and 'literature' in tag.attrs.get('data-test-id', ''))#soup.find_all('div', {'data-test-id': 'literature-results-item'})
    filtered_entries = filter_valid_entries(entries)
    
    # Lists to store data
    titles = []
    authors = []
    eprint_numbers = []
    arxiv_categories = []
    dois = []
    citation_counts = []
    
    # Extract details from each entry
    for entry in filtered_entries:
        
        title = extract_title_with_latex(entry)
        titles.append(title)

        # Extract authors using the new function
        authors_names = extract_authors(entry)
        authors.append(authors_names)
        
        # Extract eprint number
        eprint_number = extract_eprint_number(entry)
        arxiv_category = extract_arxiv_category_v2(entry)
        
        # Extract DOI
        doi = extract_doi(entry)
        citation_count = extract_citation_count_v2(entry)

        eprint_numbers.append(eprint_number)
        arxiv_categories.append(arxiv_category)
        dois.append(doi)
        citation_counts.append(citation_count)

    # Create a DataFrame from the extracted data
    data = pd.DataFrame({
        'Title': titles,
        'Authors': authors,
        'ePrint Number': eprint_numbers,
        'arXiv Category': arxiv_categories,
        'DOI': dois,
        'Citation Count': citation_counts
    })

    return data

def scrape_all_pages(driver, full_query_url):
    all_data = pd.DataFrame()

    # Prepare the base URL by removing the 'page' parameter
    base_url = prepare_base_url(full_query_url)

    # Get the total number of pages
    total_pages = get_total_pages_from_inspire(driver, full_query_url)

    for page in range(1, total_pages + 1):
        # Replace or add the 'page' parameter in the URL
        page_url = re.sub(r"(page=\d+)", f"page={page}", base_url)
        if "page=" not in page_url:
            page_url += f"&page={page}"
            
        driver.get(page_url)
        
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load. Adjust the wait time as needed.
        time.sleep(3)  # Example: using a static wait time

        html_content = driver.page_source
        #print(html_content)
        
        # Scrape the data from the current page
        page_data = scrape_page_data(html_content)

        # Concatenate the data from this page to the overall data
        all_data = pd.concat([all_data, page_data], ignore_index=True)

    return all_data

def add_abstracts(df, eprint_column='ePrint Number'):
    """
    Fetches abstracts for each paper in the DataFrame and adds them as a new column.

    Args:
    df (pandas.DataFrame): DataFrame containing paper details.
    eprint_column (str): Column name in df that contains the ePrint numbers.

    Returns:
    pandas.DataFrame: Updated DataFrame with a new column 'Abstract'.
    """
    def fetch_and_add_abstract(row):
        try:
            return fetch_abstract(row[eprint_column])
        except Exception as e:
            return "Error fetching abstract"

    df['Abstract'] = df.apply(fetch_and_add_abstract, axis=1)
    return df

def plot_arxiv_category_distribution(df, category_col='arXiv Category'):
    plt.figure(figsize=(10, 6))
    sns.countplot(y=df[category_col], order=df[category_col].value_counts().index)
    plt.title('Distribution of Papers Across arXiv Categories')
    plt.xlabel('Number of Papers')
    plt.ylabel('arXiv Category')
    plt.show()

def plot_citations_per_category(df, category_col='arXiv Category', citation_col='Citation Count'):
    plt.figure(figsize=(10, 6))
    df.groupby(category_col)[citation_col].sum().sort_values().plot(kind='barh')
    plt.title('Total Number of Citations per arXiv Category')
    plt.xlabel('Total Citations')
    plt.ylabel('arXiv Category')
    plt.show()

def plot_pareto_authors(df, authors_col='Authors', top_n=20):
    # Splitting author names, flattening the list, and counting occurrences
    authors_series = df[authors_col].dropna().str.split(', ')
    authors_flat_list = [author for sublist in authors_series for author in sublist]
    author_counts = Counter(authors_flat_list)

    # Creating a DataFrame from the counter
    authors_df = pd.DataFrame.from_dict(author_counts, orient='index', columns=['Publication Count'])
    authors_df = authors_df.sort_values(by='Publication Count', ascending=False).head(top_n)

    # Plotting the Pareto chart
    plt.figure(figsize=(10, 6))
    sns.barplot(x=authors_df['Publication Count'], y=authors_df.index)
    plt.title(f'Top {top_n} Authors by Number of Publications')
    plt.xlabel('Number of Publications')
    plt.ylabel('Author')
    plt.show()
    
def calculate_h_index(citation_counts):
    """
    Calculate the h-index for a given set of citation counts.

    Args:
    citation_counts (list or pandas.Series): A list or Series of citation counts for each paper.

    Returns:
    int: The h-index value.
    """
    sorted_counts = sorted(citation_counts, reverse=True)
    h_index = 0
    for count in sorted_counts:
        if count >= h_index + 1:
            h_index += 1
        else:
            break
    return h_index
