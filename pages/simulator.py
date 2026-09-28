# dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import time

# Import the model - if there are issues, we'll create a fallback
try:
    from model import BankClientModel, SECTORS, RETAIL_SECTORS, CORPORATE_SECTORS
except ImportError:
    st.warning("Model module not found. Using simulation mode with sample data.")
    
    # Fallback definitions
    RETAIL_SECTORS = ["Retail", "Personal Services", "Hospitality", "Education"]
    CORPORATE_SECTORS = ["Manufacturing", "Technology", "Finance", "Healthcare", "Construction", "Logistics"]
    SECTORS = RETAIL_SECTORS + CORPORATE_SECTORS + ["Unknown"]
    
    # Create a simple mock model class
    class BankClientModel:
        def __init__(self, **kwargs):
            self.datacollector = MockDataCollector()
        
        def step(self):
            pass

    class MockDataCollector:
        def get_model_vars_dataframe(self):
            months = 12
            return pd.DataFrame({
                'adoption_rate': np.linspace(0.1, 0.7, months),
                'churned_cum': np.linspace(0, 50, months),
                'avg_satisfaction': np.linspace(0.6, 0.8, months)
            })
        
        def get_agent_vars_dataframe(self):
            # Create sample agent data with more variety for 3D visualization
            agents = 200
            np.random.seed(42)
            return pd.DataFrame({
                'satisfaction': np.random.uniform(0.3, 0.95, agents),
                'products': np.random.randint(0, 5, agents),
                'channel': np.random.choice(["branch", "digital", "hybrid", "direct_sales"], agents),
                'sector': np.random.choice(SECTORS, agents),
                'adopted': np.random.choice([True, False], agents, p=[0.4, 0.6]),
                'churned': np.random.choice([True, False], agents, p=[0.1, 0.9]),
                'is_retail': np.random.choice([True, False], agents, p=[0.7, 0.3])
            })

# Function to create clusters - FIXED VERSION
def create_clusters(adf, n_clusters=5):
    """Create client clusters based on behavior patterns"""
    try:
        # Prepare features for clustering
        features = adf.copy()
        
        # Display what features are available for clustering
        available_features = [col for col in features.columns if col in ['satisfaction', 'products', 'channel', 'sector', 'adopted', 'churned', 'is_retail']]
        st.sidebar.info(f"Features available for clustering: {', '.join(available_features)}")
        
        # Convert categorical variables to numerical with proper encoding
        if 'channel' in features.columns:
            # Get all unique channels and create mapping
            unique_channels = features['channel'].unique()
            channel_mapping = {channel: i for i, channel in enumerate(unique_channels)}
            features['channel_encoded'] = features['channel'].map(channel_mapping).fillna(0)
        
        if 'sector' in features.columns:
            # Get all unique sectors and create mapping
            unique_sectors = features['sector'].unique()
            sector_mapping = {sector: i for i, sector in enumerate(unique_sectors)}
            features['sector_encoded'] = features['sector'].map(sector_mapping).fillna(0)
        
        # Convert boolean to numerical
        if 'adopted' in features.columns:
            features['adopted_encoded'] = features['adopted'].astype(int)
        if 'churned' in features.columns:
            features['churned_encoded'] = features['churned'].astype(int)
        if 'is_retail' in features.columns:
            features['is_retail_encoded'] = features['is_retail'].astype(int)
        
        # Select features for clustering - prioritize these features
        cluster_features = []
        feature_weights = {}
        
        if 'satisfaction' in features.columns:
            cluster_features.append('satisfaction')
            feature_weights['satisfaction'] = 1.5  # Higher weight for satisfaction
        
        if 'products' in features.columns:
            cluster_features.append('products')
            feature_weights['products'] = 1.2  # Higher weight for product count
        
        if 'channel_encoded' in features.columns:
            cluster_features.append('channel_encoded')
            feature_weights['channel_encoded'] = 1.0
        
        if 'sector_encoded' in features.columns:
            cluster_features.append('sector_encoded')
            feature_weights['sector_encoded'] = 1.0
        
        if 'adopted_encoded' in features.columns:
            cluster_features.append('adopted_encoded')
            feature_weights['adopted_encoded'] = 1.3  # Higher weight for adoption
        
        if 'churned_encoded' in features.columns:
            cluster_features.append('churned_encoded')
            feature_weights['churned_encoded'] = 1.3  # Higher weight for churn
        
        if 'is_retail_encoded' in features.columns:
            cluster_features.append('is_retail_encoded')
            feature_weights['is_retail_encoded'] = 1.0
        
        st.sidebar.info(f"Using {len(cluster_features)} features for clustering: {', '.join(cluster_features)}")
        
        if len(cluster_features) < 2:
            st.warning("Not enough features for clustering. Using random clusters.")
            return np.random.randint(0, n_clusters, len(features))
        
        # Prepare data for clustering
        X = features[cluster_features].fillna(0)
        
        # Apply feature weights
        weights = np.array([feature_weights.get(feat, 1.0) for feat in cluster_features])
        X_weighted = X * weights
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_weighted)
        
        # Apply K-means clustering with increased max_iter
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20, max_iter=300)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Calculate cluster sizes
        cluster_sizes = pd.Series(clusters).value_counts().sort_index()
        st.sidebar.info(f"Cluster sizes: {dict(cluster_sizes)}")
        
        return clusters
        
    except Exception as e:
        st.error(f"Clustering failed: {str(e)}")
        # Fallback: random clusters
        return np.random.randint(0, n_clusters, len(adf))

# Function to show feature importance in clustering - FIXED VERSION
def show_cluster_features_importance(adf_with_clusters, cluster_features):
    """Show which features are most important for each cluster"""
    st.subheader("📊 Feature Importance in Clustering")
    
    # Calculate statistics for each feature by cluster
    feature_stats = []
    
    for feature in cluster_features:
        if feature in adf_with_clusters.columns:
            # Check if feature is numeric or categorical
            if pd.api.types.is_numeric_dtype(adf_with_clusters[feature]):
                # For numeric features, calculate mean
                means = adf_with_clusters.groupby('cluster')[feature].mean()
                feature_stats.append((feature, means, 'mean'))
            else:
                # For categorical features, calculate mode (most frequent value)
                modes = adf_with_clusters.groupby('cluster')[feature].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A')
                feature_stats.append((feature, modes, 'mode'))
    
    # Display as a table for numeric features
    numeric_features = [(feat, stats) for feat, stats, stat_type in feature_stats if stat_type == 'mean']
    categorical_features = [(feat, stats) for feat, stats, stat_type in feature_stats if stat_type == 'mode']
    
    if numeric_features:
        st.write("**Numeric Features (Mean Values)**")
        importance_df = pd.DataFrame({feat: stats for feat, stats in numeric_features})
        importance_df = importance_df.T  # Transpose to have features as rows
        
        # Normalize to see relative importance
        importance_normalized = importance_df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)
        
        st.dataframe(importance_normalized.style.background_gradient(cmap='viridis', axis=1))
    
    if categorical_features:
        st.write("**Categorical Features (Most Frequent Values)**")
        categorical_df = pd.DataFrame({feat: stats for feat, stats in categorical_features})
        categorical_df = categorical_df.T  # Transpose to have features as rows
        st.dataframe(categorical_df)
    
    return feature_stats

# Set up the page
st.set_page_config(page_title="Banking Product Adoption Simulation", layout="wide")

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'mdf' not in st.session_state:
    st.session_state.mdf = None
if 'adf' not in st.session_state:
    st.session_state.adf = None

# Sidebar
st.sidebar.header("Banking Products")
product = st.sidebar.selectbox("Select Product", ["business_loan", "credit_line", "insurance", "savings_account"])

st.sidebar.header("Client Segmentation")
client_type = st.sidebar.radio("Client Type", ["All", "Retail", "Corporate"])

st.sidebar.header("Campaign Settings")
campaign_channel = st.sidebar.selectbox("Campaign Channel", ["branch", "digital", "hybrid", "direct_sales"])

# Target sector options
if client_type == "Retail":
    target_options = ["All Retail"] + RETAIL_SECTORS
elif client_type == "Corporate":
    target_options = ["All Corporate"] + CORPORATE_SECTORS
else:
    target_options = ["All"] + SECTORS

target_sector = st.sidebar.selectbox("Target Sector", target_options)
discount_pct = st.sidebar.slider("Discount/Incentive (%)", 0.0, 0.5, 0.10, 0.01)
budget = st.sidebar.number_input("Campaign Budget (DT)", 10000, 5000000, 300000, 10000)

st.sidebar.header("Market Scenario")
market_scenario = st.sidebar.selectbox("Scenario", [
    "baseline", "currency_devaluation", "digital_transformation",
    "export_boom", "regional_instability", "economic_growth", "recession"
])

st.sidebar.header("Simulation Parameters")
steps = st.sidebar.slider("Months to simulate", 3, 36, 12)
N = st.sidebar.slider("Total Businesses", 100, 2000, 500, 50)
retail_ratio = st.sidebar.slider("Retail/Corporate Ratio", 0.0, 1.0, 0.7, 0.05)

# Cluster settings
n_clusters = st.sidebar.slider("Number of Clusters", 2, 6, 5)

run = st.sidebar.button("Run Simulation", type="primary")

# Main content
st.title("🏦 Banking Product Adoption Simulation")

if run:
    with st.spinner("Running simulation..."):
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize model
        model = BankClientModel(
            N=N, width=20, height=20,
            campaign_channel=campaign_channel,
            target_sector=target_sector,
            discount_pct=discount_pct,
            market_scenario=market_scenario,
            retail_ratio=retail_ratio
        )
        
        # Run simulation steps
        for i in range(steps):
            model.step()
            progress = (i + 1) / steps
            progress_bar.progress(progress)
            status_text.text(f"Simulating month {i+1} of {steps}...")
            time.sleep(0.1)  # Simulate processing time
        
        # Get results
        mdf = model.datacollector.get_model_vars_dataframe()
        adf = model.datacollector.get_agent_vars_dataframe()
        
        # Store in session state
        st.session_state.model = model
        st.session_state.mdf = mdf
        st.session_state.adf = adf
        
        progress_bar.empty()
        status_text.empty()
        
        st.success("Simulation completed successfully!")

# Display results if available
if st.session_state.mdf is not None:
    mdf = st.session_state.mdf
    adf = st.session_state.adf
    
    # Filter by client type if needed
    if client_type == "Retail":
        adf = adf[adf['is_retail'] == True]
    elif client_type == "Corporate":
        adf = adf[adf['is_retail'] == False]
    
    # Calculate metrics
    total_clients = len(adf)
    adoption_rate = mdf['adoption_rate'].iloc[-1] * 100 if 'adoption_rate' in mdf.columns else 35.0
    avg_satisfaction = mdf['avg_satisfaction'].iloc[-1] if 'avg_satisfaction' in mdf.columns else 0.75
    churned_count = mdf['churned_cum'].iloc[-1] if 'churned_cum' in mdf.columns else 25
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Clients", total_clients)
    col2.metric("Adoption Rate", f"{adoption_rate:.1f}%")
    col3.metric("Avg Satisfaction", f"{avg_satisfaction:.2f}")
    col4.metric("Churned Clients", int(churned_count))
    
    # Create clusters
    adf_clustered = adf.copy()
    adf_clustered['cluster'] = create_clusters(adf, n_clusters=n_clusters)
    
    # Show feature importance
    cluster_features = ['satisfaction', 'products', 'channel', 'sector', 'adopted', 'churned', 'is_retail']
    available_features = [f for f in cluster_features if f in adf_clustered.columns]
    
    # 3D Visualization Section - Focus on Clusters
    st.subheader("🔭 3D Cluster Analysis")
    
    # Prepare data for 3D visualization
    adf_3d = adf_clustered.copy()
    
    # Generate features for 3D visualization
    np.random.seed(42)
    adf_3d['Product_Usage'] = adf_3d['products'] if 'products' in adf_3d.columns else np.random.randint(0, 5, len(adf_3d))
    adf_3d['Engagement_Score'] = adf_3d['satisfaction'] * 10 if 'satisfaction' in adf_3d.columns else np.random.uniform(3, 10, len(adf_3d))
    adf_3d['Loyalty_Score'] = adf_3d['satisfaction'] * 100 if 'satisfaction' in adf_3d.columns else np.random.uniform(30, 95, len(adf_3d))
    
    # Create tabs for different cluster views
    tab1, tab2, tab3, tab4 = st.tabs(["Cluster Overview", "Cluster Characteristics", "Cluster Performance", "Feature Importance"])
    
    with tab1:
        # Main 3D cluster visualization
        fig_3d_clusters = px.scatter_3d(
            adf_3d,
            x='Product_Usage',
            y='Engagement_Score',
            z='Loyalty_Score',
            color='cluster',
            hover_data=['sector', 'channel', 'adopted', 'churned'],
            title='3D Client Clusters: Product Usage vs Engagement vs Loyalty',
            labels={
                'Product_Usage': 'Number of Products',
                'Engagement_Score': 'Engagement Level',
                'Loyalty_Score': 'Loyalty Score',
                'cluster': 'Client Cluster'
            }
        )
        st.plotly_chart(fig_3d_clusters, use_container_width=True)
    
    with tab2:
        # Cluster characteristics by sector and channel
        col1, col2 = st.columns(2)
        
        with col1:
            if 'sector' in adf_3d.columns:
                sector_cluster = pd.crosstab(adf_3d['sector'], adf_3d['cluster'])
                fig_sector = px.imshow(sector_cluster, 
                                     title="Cluster Distribution by Sector",
                                     labels=dict(x="Cluster", y="Sector", color="Count"))
                st.plotly_chart(fig_sector, use_container_width=True)
        
        with col2:
            if 'channel' in adf_3d.columns:
                channel_cluster = pd.crosstab(adf_3d['channel'], adf_3d['cluster'])
                fig_channel = px.imshow(channel_cluster, 
                                      title="Cluster Distribution by Channel",
                                      labels=dict(x="Cluster", y="Channel", color="Count"))
                st.plotly_chart(fig_channel, use_container_width=True)
    
    with tab3:
        # Cluster performance metrics
        cluster_stats_df = adf_3d.groupby('cluster').agg({
            'satisfaction': 'mean',
            'products': 'mean',
            'adopted': 'mean',
            'churned': 'mean'
        }).round(3)
        
        cluster_stats_df.columns = ['Avg Satisfaction', 'Avg Products', 'Adoption Rate', 'Churn Rate']
        
        # Display cluster performance
        st.subheader("Cluster Performance Metrics")
        st.dataframe(cluster_stats_df)
        
        # Performance comparison chart
        fig_performance = go.Figure()
        
        for metric in ['Avg Satisfaction', 'Adoption Rate']:
            if metric in cluster_stats_df.columns:
                fig_performance.add_trace(go.Bar(
                    x=cluster_stats_df.index,
                    y=cluster_stats_df[metric],
                    name=metric,
                    text=cluster_stats_df[metric].round(2),
                    textposition='auto'
                ))
        
        fig_performance.update_layout(
            title="Cluster Performance Comparison",
            xaxis_title="Cluster",
            yaxis_title="Score",
            barmode='group'
        )
        st.plotly_chart(fig_performance, use_container_width=True)
    
    with tab4:
        # Feature importance analysis
        if available_features:
            importance_df = show_cluster_features_importance(adf_clustered, available_features)
        else:
            st.warning("Not enough features available for importance analysis.")
    
    # Client distribution charts
    st.subheader("Client Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cluster distribution
        cluster_counts = adf_3d['cluster'].value_counts().reset_index()
        cluster_counts.columns = ['Cluster', 'Count']
        fig_cluster = px.pie(cluster_counts, values='Count', names='Cluster', 
                           title="Client Distribution by Cluster")
        st.plotly_chart(fig_cluster, use_container_width=True)
    
    with col2:
        # Channel distribution
        if 'channel' in adf.columns:
            channel_counts = adf['channel'].value_counts().reset_index()
            channel_counts.columns = ['Channel', 'Count']
            fig_channel = px.bar(channel_counts, x='Channel', y='Count', 
                                title="Clients by Channel", color='Channel')
            st.plotly_chart(fig_channel, use_container_width=True)
    
    # Data preview
    with st.expander("View Sample Data with Clusters"):
        if 'sector' in adf_3d.columns and 'channel' in adf_3d.columns:
            st.dataframe(adf_3d[['cluster', 'sector', 'channel', 'products', 'adopted', 'churned']].head(10))

else:
    # Welcome message and instructions
    st.info("""
    ## Welcome to our banking Simulator
    
    This tool helps you simulate how different client segments respond to banking products 
    under various market conditions.
    
    **To get started:**
    1. Configure your campaign settings in the sidebar
    2. Select your target client segment
    3. Choose a market scenario
    4. Adjust simulation parameters
    5. Click **Run Simulation** to see the results
    
    The simulator will model adoption rates, churn, and client satisfaction based on your settings.
    """)
    
    # Sample 3D cluster visualization for demonstration
    st.subheader("🔭 Sample 3D Cluster Analysis Preview")
    
    # Create sample 3D data with clusters
    np.random.seed(42)
    sample_size = 100
    sample_data = pd.DataFrame({
        'Product_Usage': np.random.randint(0, 5, sample_size),
        'Engagement_Score': np.random.uniform(3, 10, sample_size),
        'Loyalty_Score': np.random.uniform(30, 95, sample_size),
        'cluster': np.random.randint(0, 5, sample_size),
        'Adopted': np.random.choice([True, False], sample_size, p=[0.4, 0.6])
    })
    
    fig_sample = px.scatter_3d(
        sample_data,
        x='Product_Usage',
        y='Engagement_Score',
        z='Loyalty_Score',
        color='cluster',
        title='Sample 3D Client Clusters',
        labels={
            'Product_Usage': 'Number of Products',
            'Engagement_Score': 'Engagement Level',
            'Loyalty_Score': 'Loyalty Score',
            'cluster': 'Client Cluster'
        }
    )
    st.plotly_chart(fig_sample, use_container_width=True)
    
    st.info("Run the simulation to see interactive 3D cluster analysis of your client data!")

# Footer
st.markdown("---")
st.caption("Banking Product Adoption Simulator v1.0 | Built with Streamlit")