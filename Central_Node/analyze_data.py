import pandas as pd
import matplotlib.pyplot as plt


def plot_csv_columns_together(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Check if the CSV file has at least 3 columns
    if df.shape[1] < 3:
        print("The CSV file does not have at least 3 columns.")
        return
    
    # Plot all three columns in a single plot
    plt.figure(figsize=(10, 6))
    
    for column in df.columns[:3]:
        plt.plot(df[column], label=column)
    
    plt.title('Values of Node 0')
    plt.xlabel('time')
    plt.ylabel('percent/°C')
    plt.legend()
    plt.grid(True)
    
    # Show the plot
    plt.show()

# Example usage
file_path = 'data/node0.csv'  # Replace with the path to your CSV file
plot_csv_columns_together(file_path)