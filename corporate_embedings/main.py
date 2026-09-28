from data_loader import load_corporate_data

if __name__ == "__main__":
    # Charger toutes les données Corporate
    corporate_df = load_corporate_data()
    print("Corporate data loaded:", corporate_df.shape)
    print(corporate_df.head())
