import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import numpy as np

# --- Data inside Python (no CSV needed) ---
data = {
    'Direction Régionale': [
        'tunis','ariana','ben arous','bizerte','gabes','gafsa','jendouba','kairouan',
        'kasserine','kef','mahdia','mannouba','medenine','monastir','nabeul','sfax',
        'sidi bouzid','siliana','sousse','tataouine','tozeur','zaghouan'
    ],
    'count': [
        1750, 300, 420, 600, 480, 800, 270, 2337, 950, 310,
        720, 400, 520, 1100, 1350, 1900, 870, 290, 1200, 450, 250, 330
    ]
}

combined_df = pd.DataFrame(data)

# --- Coordinates of each region ---
direction_coords = {
    'tunis': [36.8, 10.2],
    'ariana': [36.9, 10.1],
    'ben arous': [36.7, 10.3],
    'bizerte': [37.3, 9.9],
    'gabes': [33.9, 10.1],
    'gafsa': [34.4, 8.8],
    'jendouba': [36.5, 8.8],
    'kairouan': [35.7, 10.1],
    'kasserine': [35.2, 8.8],
    'kef': [36.2, 8.7],
    'mahdia': [35.5, 11.0],
    'mannouba': [36.8, 10.1],
    'medenine': [33.3, 10.5],
    'monastir': [35.8, 10.8],
    'nabeul': [36.5, 10.7],
    'sfax': [34.7, 10.8],
    'sidi bouzid': [35.0, 9.5],
    'siliana': [36.1, 9.3],
    'sousse': [35.8, 10.6],
    'tataouine': [32.9, 10.4],
    'tozeur': [33.9, 8.1],
    'zaghouan': [36.4, 10.1]
}

# Clean names for matching
combined_df['direction_clean'] = combined_df['Direction Régionale'].str.strip().str.lower()

# Add coordinates column
combined_df['coords'] = combined_df['direction_clean'].map(direction_coords)

# --- Sample Corporate Data ---
corporate_data = {
    'gouvernorate': [
        'tunis', 'tunis', 'sfax', 'sousse', 'nabeul', 'tunis', 'sfax', 'monastir',
        'ben arous', 'ariana', 'bizerte', 'gabes', 'gafsa', 'jendouba', 'kairouan',
        'kasserine', 'kef', 'mahdia', 'mannouba', 'medenine', 'sidi bouzid', 'siliana',
        'tataouine', 'tozeur', 'zaghouan', 'tunis', 'sfax', 'sousse'
    ],
    'delegation': [
        'bab bhar', 'cite jardins', 'sfax ville', 'sousse jawhra', 'nabeul ville', 
        'lafayette', 'sakiet ezzit', 'monastir ville', 'mornag', 'ariana ville',
        'bizerte nord', 'gabes ouest', 'gafsa sud', 'jendouba ville', 'kairouan ville',
        'kasserine ville', 'kef ville', 'mahdia ville', 'mannouba ville', 'medenine ville',
        'sidi bouzid ouest', 'siliana ville', 'tataouine ville', 'tozeur ville', 'zaghouan ville',
        'menzah', 'sakiet eddaier', 'kalaa seghira'
    ],
    'company_type': [
        'Retail', 'Corporate', 'Corporate', 'Retail', 'Retail', 'Corporate', 'Corporate', 'Retail',
        'Retail', 'Corporate', 'Retail', 'Corporate', 'Retail', 'Retail', 'Corporate', 'Retail',
        'Retail', 'Corporate', 'Retail', 'Corporate', 'Retail', 'Retail', 'Corporate', 'Retail',
        'Corporate', 'Corporate', 'Retail', 'Corporate'
    ]
}

corporate_df = pd.DataFrame(corporate_data)

# --- Streamlit app ---
st.title("📍 Map of Tunisia - Regional & Corporate Data")
st.markdown("### Distribution of counts across different regions and corporate entities")

# Create tabs for different views
tab1, tab2 = st.tabs(["Regional Distribution", "Corporate Distribution"])

with tab1:
    # Display the data table
    with st.expander("View Raw Data"):
        st.dataframe(combined_df)

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Center map on Tunisia
        m = folium.Map(location=[34.0, 9.5], zoom_start=6)
        
        # Define a color palette based on count values
        max_count = combined_df['count'].max()
        min_count = combined_df['count'].min()
        
        # Add points for each region
        for _, row in combined_df.iterrows():
            if row['coords'] is not None:
                # Calculate color based on count (red for high, blue for low)
                normalized_count = (row['count'] - min_count) / (max_count - min_count)
                red = int(255 * normalized_count)
                blue = int(255 * (1 - normalized_count))
                color = f"#{red:02x}00{blue:02x}"
                
                folium.CircleMarker(
                    location=row['coords'],
                    radius=10 + (row['count'] / 100),  # size based on count
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=f"{row['Direction Régionale'].title()}: {row['count']}",
                    tooltip=f"{row['Direction Régionale'].title()}: {row['count']}"
                ).add_to(m)
                
                # Add a text label with the count
                folium.Marker(
                    location=row['coords'],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size: 12pt; font-weight: bold; color: {color}">{row["count"]}</div>'
                    ),
                    tooltip=row['Direction Régionale'].title()
                ).add_to(m)

        # Display the map in Streamlit
        st_data = st_folium(m, width=600, height=500)

    with col2:
        st.markdown("### Counts by Region")
        
        # Sort by count for better visualization
        sorted_df = combined_df.sort_values('count', ascending=False)
        
        # Display as a bar chart
        st.bar_chart(sorted_df.set_index('Direction Régionale')['count'])
        
        # Show summary statistics
        st.metric("Total Count", combined_df['count'].sum())
        st.metric("Average Count", round(combined_df['count'].mean(), 1))
        st.metric("Highest Count", f"{sorted_df.iloc[0]['Direction Régionale']}: {sorted_df.iloc[0]['count']}")
        st.metric("Lowest Count", f"{sorted_df.iloc[-1]['Direction Régionale']}: {sorted_df.iloc[-1]['count']}")

    # Add some analysis
    st.markdown("---")
    st.markdown("### Regional Distribution ")

    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Regions with >1000", len(combined_df[combined_df['count'] > 1000]))
        
    with col2:
        st.metric("Regions with 500-1000", len(combined_df[(combined_df['count'] >= 500) & (combined_df['count'] <= 1000)]))
        
    with col3:
        st.metric("Regions with <500", len(combined_df[combined_df['count'] < 500]))

    # Color explanation
    st.info("""
    **Map Legend:**
    - Larger circles indicate higher counts
    - Redder colors indicate higher counts
    - Bluer colors indicate lower counts
    - Numbers show the exact count for each region
    """)

with tab2:
    st.header("Corporate & Retail Distribution")
    
    # --- Corporate Data Processing ---
    corporate_df['gouvernorate_clean'] = corporate_df['gouvernorate'].str.strip().str.lower()
    corporate_df['delegation_clean'] = corporate_df['delegation'].str.strip().str.lower()
    
    # Count companies by governorate
    counts_gouv = corporate_df.groupby('gouvernorate_clean').size().reset_index(name='count')
    
    # Count by company type
    company_type_counts = corporate_df.groupby('company_type').size().reset_index(name='count')
    
    # Display corporate data
    with st.expander("View Corporate Data"):
        st.dataframe(corporate_df)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create corporate map
        st.subheader("Corporate Distribution Map")
        
        # Define color palette
        palette = ["#012a4a","#013a63","#01497c","#014f86","#2a6f97","#2c7da0","#468faf","#61a5c2","#89c2d9","#a9d6e5"]
        
        min_count = counts_gouv['count'].min()
        max_count = counts_gouv['count'].max()
        
        def get_color(count):
            idx = int((count - min_count) / (max_count - min_count) * (len(palette) - 1))
            return palette[min(idx, len(palette)-1)]
        
        # Create map
        m_corp = folium.Map(location=[34.0, 9.0], zoom_start=6, tiles='CartoDB positron')
        
        # Add MarkerCluster
        marker_cluster = MarkerCluster().add_to(m_corp)
        
        # Add circles for each governorate
        for index, row in counts_gouv.iterrows():
            gouv = row['gouvernorate_clean']
            count = row['count']
            
            if gouv in direction_coords:
                lat, lon = direction_coords[gouv]
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5 + count/2,  # Adjust based on density
                    color=get_color(count),
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"{gouv.title()}\nNumber of companies: {count}",
                    tooltip=f"{gouv.title()}: {count}"
                ).add_to(marker_cluster)
        
        # Display the map
        st_folium(m_corp, width=600, height=500)
    
    with col2:
        st.subheader("Statistics")
        
        # Display governorate counts
        st.markdown("**By Governorate**")
        st.dataframe(counts_gouv.sort_values('count', ascending=False))
        
        # Metrics
        st.metric("Total Companies", counts_gouv['count'].sum())
        st.metric("Corporate Entities", company_type_counts[company_type_counts['company_type'] == 'Corporate']['count'].values[0])
        st.metric("Retail Entities", company_type_counts[company_type_counts['company_type'] == 'Retail']['count'].values[0])
    
    # Additional analysis
    st.markdown("---")
    st.subheader("Corporate Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top Governorates by Company Count**")
        top_gouvs = counts_gouv.nlargest(5, 'count')
        for _, row in top_gouvs.iterrows():
            st.write(f"- {row['gouvernorate_clean'].title()}: {row['count']} companies")
    
    with col2:
        st.markdown("**Company Type Distribution**")
        corp_count = company_type_counts[company_type_counts['company_type'] == 'Corporate']['count'].values[0]
        retail_count = company_type_counts[company_type_counts['company_type'] == 'Retail']['count'].values[0]
        total = corp_count + retail_count
        
        st.write(f"- Corporate: {corp_count} ({corp_count/total*100:.1f}%)")
        st.write(f"- Retail: {retail_count} ({retail_count/total*100:.1f}%)")