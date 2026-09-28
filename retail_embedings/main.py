from data_loader import load_retail_data

if __name__ == "__main__":
    retail_df = load_retail_data()
    print(retail_df.head())
