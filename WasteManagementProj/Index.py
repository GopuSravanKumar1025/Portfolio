import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#Found Dataset at https://www.data.gov.uk/dataset/0e0c12d8-24f6-461f-b4bc-f6d6a5bf2de5/wastedataflow-local-authority-waste-management/datafile/9950ae3d-5957-4f6c-a408-e1abbf490216/preview

class Data:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.filtered_df = None
        self.graphs_dir = 'Graphs'
        if not os.path.exists(self.graphs_dir):
            os.makedirs(self.graphs_dir)

    def load_data(self):
        if self.file_path is None:
            raise ValueError("File path not set. Ensure the file exists and was provided.")
        self.df = pd.read_csv(self.file_path, skiprows=1, low_memory=False)

    def filter_data(self, cities_councils):
        facility_col = 'FacilityAddress'
        tonnes_col = 'TotalTonnes'
        period_col = 'Period'
        material_col = 'Material'
        if facility_col not in self.df.columns or tonnes_col not in self.df.columns or period_col not in self.df.columns or material_col not in self.df.columns:
            raise KeyError(f"One or more columns not found. Check if '{facility_col}', '{tonnes_col}', '{period_col}', '{material_col}' are present in the DataFrame.")
        self.df[tonnes_col] = pd.to_numeric(self.df[tonnes_col], errors='coerce')
        self.filtered_df = self.df[self.df[facility_col].str.contains('|'.join(cities_councils), case=False, na=False)]
        if self.filtered_df.empty:
            print("No data found for the specified cities or councils.")
        else:
            return self.filtered_df

    def plot_charts(self):
        if self.filtered_df is None or self.filtered_df.empty:
            print("No filtered data available to plot.")
            return
        facility_col = 'FacilityAddress'
        tonnes_col = 'TotalTonnes'
        period_col = 'Period'
        material_col = 'Material'

        # Bar chart for total tonnes by material
        material_totals = self.filtered_df.groupby(period_col)[tonnes_col].sum()
        plt.figure(figsize=(10, 7))
        material_totals.sort_values().plot(kind='barh', color='skyblue')
        plt.xlabel('Total Tonnes')
        plt.ylabel('Period')
        plt.title('Total Tonnes by Material (Filtered)')
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'total_tonnes_by_material.png'))
        plt.show()
        plt.close()

        # Stacked bar chart for total tonnes by material and period
        stacked_data = self.filtered_df.groupby([period_col, material_col])[tonnes_col].sum().unstack()
        plt.figure(figsize=(16, 20))
        ax = stacked_data.plot(kind='bar', stacked=True)
        plt.xlabel('Period')
        plt.ylabel('Total Tonnes')
        plt.title('Total Tonnes by Material and Period (Stacked)')
        plt.xticks(rotation=45)  
        plt.legend(title='Material', bbox_to_anchor=(-0.2, 1), loc='upper right')
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'total_tonnes_by_material.png'))
        plt.show()
        plt.close()

        # Heatmap of total tonnes by material and period
        heatmap_data = self.filtered_df.pivot_table(index=period_col, columns=material_col, values=tonnes_col, aggfunc='sum')
        plt.figure(figsize=(14, 8))
        sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='.1f', linewidths=.5)
        plt.xlabel('Material')
        plt.ylabel('Period')
        plt.title('Heatmap of Total Tonnes by Material and Period')
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'heatmap_total_tonnes.png'))
        plt.show()
        plt.close()

    def check_missing_values(self):
        if self.df is None:
            raise ValueError("Data not loaded. Please load the data first.")
        missing_values = self.df.isnull().sum()
        print("Missing values in each column:\n", missing_values)
        return missing_values

    def check_unique_values(self):
        if self.df is None:
            raise ValueError("Data not loaded. Please load the data first.")
        unique_values = {col: self.df[col].unique() for col in self.df.columns}
        for col, values in unique_values.items():
            print(f"Unique values in '{col}':\n{values}\n")
        return unique_values

    @staticmethod
    def Index():
        file_path = 'Datasets/Q100_Waste_collection_data_England_2022_23.csv'
        cities_councils = [
            'Aberafan', 'Bangor', 'Aberdare', 'Caer', 'Cardiff', 'Cnwch coch', 'Conwy',
            'Cwm', 'Swansea', 'Abergwaun', 'Abertawe', 'Bala', 'Beddgelert', 'Betws',
            'Coed', 'Abergavenny', 'Abergele', 'wrexham'
        ]
        visualizer = Data(file_path)
        visualizer.load_data()
        filtered_data = visualizer.filter_data(cities_councils)
        visualizer.plot_charts()
        visualizer.check_missing_values()
        visualizer.check_unique_values()