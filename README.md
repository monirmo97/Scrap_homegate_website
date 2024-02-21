Real Estate Scraper and Analyzer

This project is a Python script that scrapes data from Homegate.ch, a website that lists properties for rent or sale in Switzerland. It allows you to specify the type of ad (rent or buy), the city, the number of rooms, and the price range. It then collects information such as address, title, price, living space, and description for each property that matches your criteria. It also saves the data to a CSV file and generates some charts to visualize and analyze the data.

Requirements
To run this project, you need to have the following:

Python 3.6 or higher

Requests library

BeautifulSoup library

Pandas library

Matplotlib library

You can install these libraries using pip:

pip install requests
pip install beautifulsoup4
pip install pandas
pip install matplotlib

Usage:

To run this project, you need to clone or download this repository and navigate to the project folder. Then, you can use the following command-line arguments to customize your search:

--ad_type: The type of ad (rent or buy). Default is rent.

--city: The name of the city. Default is Zurich.

--room: The number of rooms. Default is 2.

--price: The maximum price. Default is 2000.

For example, if you want to scrape data for properties for rent in Geneva with 3 rooms and a maximum price of 2500, you can use this command:

python main.py --ad_type rent --city Geneva --room 3 --price 2500

The script will then scrape the data from the website and save it to a file named final_result.csv in the same folder. It will also create some charts and save them to a folder named img in the same folder. The charts are:

A scatter plot of price vs rooms

A line plot of price vs living space

A bar plot of the top 5 properties by price

A histogram of the price distribution

A box plot of the prices by rooms
A pie chart of the room distribution