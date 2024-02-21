import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

matplotlib.use('Agg')


def line_price_space(data):
    data = data.sort_values(by='Living Space (m²)')
    # Plotting Price vs. Living Space as a line chart
    plt.figure(figsize=(24, 18))
    plt.plot(data['Living Space (m²)'],
             data['Price'], marker='o', linestyle='-')
    plt.title('Price vs. Living Space')
    plt.xlabel('Living Space (m²)')
    plt.ylabel('Price')
    plt.grid(True)

    # Save the plot as an image file (e.g., PNG)
    plt.savefig('price_vs_living_space_plot.png')

    # Close the plot (optional)
    plt.close()


def scatter_price_room(data):
    plt.figure(figsize=(8, 6))
    plt.scatter(data['Rooms'], data['Price'], color='blue')
    plt.title('Price vs. Rooms')
    plt.xlabel('Rooms')
    plt.ylabel('Price')
    plt.grid(True)
    plt.savefig('price_vs_rooms_plot.png')
    plt.close()


def plot_top_price(data):
    # Get the top 5 best-selling properties based on Price
    top_price = data.nlargest(5, 'Price')

    # Plot the bar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    top_price.plot(kind='bar', x='Price', y='Living Space (m²)', color='purple', ax=ax)

    # Set plot title and labels
    ax.set_title("Top 5 by Price")
    ax.set_xlabel("Top 5 Price")
    ax.set_ylabel("Living Space (m²)")

    # Ensure tight layout and save the plot
    plt.tight_layout()
    plt.savefig('Top_5_Properties_by_Price.png')
    plt.close()


def plot_price_histogram(data):
    plt.figure(figsize=(10, 6))
    plt.hist(data['Price'], bins=20, color='blue', alpha=0.7)
    plt.title('Histogram of Prices')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig('price_histogram.png')
    plt.close()


def plot_boxplot_prices_by_rooms(data):
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='Rooms', y='Price', data=data)
    plt.title('Boxplot of Prices by Room Count')
    plt.xlabel('Rooms')
    plt.ylabel('Price')
    plt.grid(True)
    plt.savefig('boxplot_prices_by_rooms.png')
    plt.close()


def plot_pie_chart_room_distribution(data):
    room_counts = data['Rooms'].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(room_counts, labels=room_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title('Room Distribution')
    plt.savefig('pie_chart_room_distribution.png')
    plt.close()
