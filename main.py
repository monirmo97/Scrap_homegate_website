import csv
import argparse
import requests
import re
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from charts import (
    line_price_space,
    scatter_price_room,
    plot_top_price,
    plot_price_histogram,
    plot_boxplot_prices_by_rooms,
    plot_pie_chart_room_distribution
)


def clean_data(data_frame):
    """
    Clean the data by removing rows with "Price on request",
    converting 'Price' and 'Living Space (m²)' to numeric,
    dropping rows with NaN missing values, removing duplicate rows,
    and stripping unwanted characters in columns.

    Parameters:
    - data_frame (pd.DataFrame): The input DataFrame.

    Returns:
    - pd.DataFrame: Cleaned DataFrame.
    """
    data_frame = data_frame[data_frame["Price"] != " Price on request "]
    data_frame['Price'] = pd.to_numeric(data_frame['Price'], errors='coerce')
    data_frame['Living Space (m²)'] = pd.to_numeric(data_frame['Living Space (m²)'], errors='coerce')
    data_frame.dropna(inplace=True)
    data_frame.drop_duplicates(inplace=True)

    for column in data_frame.columns:
        if isinstance(data_frame[column], str):
            data_frame[column] = data_frame[column].str.strip()

    return data_frame


def generate_query_string(args, ep):
    """
    Generate a query string based on the provided arguments.

    Parameters:
    - args (argparse.Namespace): Parsed command-line arguments.
    - ep (int): Page number.

    Returns:
    - str: Query string.
    """
    params = {'ep': ep, 'ac': args.room, "ah": args.price}
    valid_params = {key: value for key, value in params.items() if value is not None}
    query_string = "&".join(f"{key}={value}" for key, value in valid_params.items())
    return query_string


def construct_basic_url(args, ep):
    """
    Construct the URL based on the provided arguments and page number.

    Parameters:
    - args (argparse.Namespace): Parsed command-line arguments.
    - ep (int): Page number.

    Returns:
    - str: Constructed URL.
    """
    base_url = f'https://www.homegate.ch/{args.ad_type}/real-estate'
    search_params = f'/city-{args.city}/matching-list?{generate_query_string(args, ep)}'
    final_url = f'{base_url}{search_params}'
    return final_url


def get_all_items(response):
    """
    Extract and return all elements with the specified tag and class from the HTML content.

    Parameters:
    - response (requests.Response): The HTTP response.

    Returns:
    - ResultSet: A ResultSet containing elements.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all('div', {'role': 'listitem', 'data-test': 'result-list-item', 'class': 'ResultList_listItem_j5Td_'})
    return elements


def extract_numeric_value(currency_string):
    """
    Extract and return the numeric value from a currency string.

    Parameters:
    - currency_string (str): The input currency string.

    Returns:
    - int or str: The extracted numeric value or the original string.
    """
    numeric_part = re.sub(r'[^\d]', '', currency_string)
    try:
        if len(numeric_part) == 0:
            return currency_string
        numeric_value = int(numeric_part)
        return numeric_value
    except Exception as err:
        print(f"Error converting {numeric_part} to a numeric value. {err}")
        return None


def extract_room_value(room):
    """
    Extract and return the numeric value from a room string.

    Parameters:
    - room (str): The input room string.

    Returns:
    - float or str: The extracted numeric value or the original string.
    """
    numeric_part = re.sub(r'[^\d.]', '', room.split('room')[0])
    try:
        if len(numeric_part) == 0:
            return room
        numeric_value = float(numeric_part)
        return numeric_value
    except ValueError:
        print(f"Error converting {numeric_part} to a numeric value.")
        return None


def extract_living_space_value(living_space):
    """
    Extract and return the living space value from a living space string.

    Parameters:
    - living_space (str): The input living space string.

    Returns:
    - str or None: The extracted living space value or None.
    """
    try:
        match = re.search(r'(\d+(\.\d+)?)\s*m²', living_space.split('room')[1])
        if match:
            numeric_value = match.group(1)
            return f"{int(numeric_value)}"
        else:
            return None
    except Exception as err:
        print("--> ", err)
        return None


def get_part_of_elements(soup):
    """
    Extract information based on class names from a BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object.

    Returns:
    - dict: A dictionary containing extracted information.
    """
    address = soup.select_one('.HgListingCard_address_JGiFv').text if soup.select_one(
        '.HgListingCard_address_JGiFv') else None
    price = soup.select_one('.HgListingCard_price_JoPAs').text if soup.select_one(
        '.HgListingCard_price_JoPAs') else None
    title = soup.select_one('.HgListingDescription_title_NAAxy').text if soup.select_one(
        '.HgListingDescription_title_NAAxy') else None
    rooms_living_space = soup.select_one('.HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq').text if soup.select_one(
        '.HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq') else None
    description = soup.select_one('.HgListingDescription_large_uKs3J').text if soup.select_one(
        '.HgListingDescription_large_uKs3J') else None

    li_tags = soup.select('ul.glide__slides li')
    imgs = []
    for li in li_tags:
        img_tag = li.select_one('img')
        if img_tag:
            src_attribute = img_tag['src']
            imgs.append(src_attribute)

    result = {
        "Address": address,
        "Price": extract_numeric_value(price),
        "Title": title,
        "Rooms": extract_room_value(str(rooms_living_space)),
        "Living Space (m²)": extract_living_space_value(str(rooms_living_space)),
        "Description": description,
        "Image": imgs[0] if imgs and len(imgs) != 0 else "",
    }

    return result


def save_list_of_dicts_to_csv(data, file_path):
    """
    Save a list of dictionaries to a CSV file.

    Parameters:
    - data (list): List of dictionaries.
    - file_path (str): Path to the CSV file.
    """
    try:
        fieldnames = list(data[0].keys())

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(data)
    except Exception as error:
        print(error)
        pass


def main():
    parser = argparse.ArgumentParser(description='Scrape real estate data from homegate.ch and generate charts.')
    parser.add_argument('--ad_type', type=str, default='rent',
                        choices=['buy', 'rent'],
                        help='Specify the type of ad (buy or rent)')
    parser.add_argument('--city', type=str, default='Zurich',
                        help='Specify the name of the city')
    parser.add_argument('--room', type=int, default=2,
                        help='Specify the number of rooms')
    parser.add_argument('--price', type=int, default=2000,
                        help='Specify the price of the house')
    parser.add_argument('--revisit_days', type=int, default=1,
                        help='Specify the number of days to revisit each detail page')
    args = parser.parse_args()

    # Initialize variables
    page = 0
    all_page_results = []
    unavailable_pages = []
    
    
    while True:
        try:
            page += 1
            # URL of the webpage
            url = construct_basic_url(args, page)

            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                items = get_all_items(response)
                if len(items) == 0:
                    break

                for item in items:
                    page_result = get_part_of_elements(item)
                    all_page_results.append(page_result)
            else:
                print(f"Error: Failed to retrieve content. Status code: {response.status_code}")
                # Add the URL to a list of unavailable pages
                unavailable_pages.append(url)
        except HTTPError as e:
            print(f"Error: Failed to retrieve content for URL: {url}. {str(e)}")
            # Add the URL to a list of unavailable pages
            unavailable_pages.append(url)

        except Exception as e:
            print(f"Error: An exception occurred while processing URL: {url}. {str(e)}")
            # Handle any other exceptions that may occur
        
        
    save_list_of_dicts_to_csv(all_page_results, 'final_result.csv')
    data = clean_data(pd.DataFrame(all_page_results).drop('Image', axis=1).drop('Description', axis=1))
    
    # plot charts
    scatter_price_room(data)
    line_price_space(data)
    plot_top_price(data)
    plot_price_histogram(data)
    plot_boxplot_prices_by_rooms(data)
    plot_pie_chart_room_distribution(data)
    
    # Print the list of unavailable pages
    print("Unavailable Pages:")
    for page_url in unavailable_pages:
        print(page_url)

if __name__ == "__main__":
    main()
