# home.py
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Banking Analytics Suite",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .objective-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        color: #333333;
        line-height: 1.6;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .get-started-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        display: block;
        margin: 2rem auto;
        text-align: center;
    }
    .get-started-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    .app-link {
        display: block;
        text-align: center;
        margin: 1rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 10px;
        font-weight: bold;
        transition: transform 0.3s ease;
    }
    .app-link:hover {
        transform: translateY(-2px);
        color: white;
        text-decoration: none;
    }
    .section-title {
        font-size: 2rem;
        color: #1f77b4;
        text-align: center;
        margin: 2rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
    }
    .platform-header {
        font-size: 1.8rem;
        color: #1f77b4;
        margin-bottom: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="main-header">🏦 Banking Analytics Suite</div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; font-size: 1.2rem; color: #555; margin-bottom: 3rem;'>
    AI-powered simulation platform for banking client behavior analysis and strategic planning
</div>
""", unsafe_allow_html=True)

# Project Overview Section
st.markdown('<div class="section-title">🎯 Project Overview</div>', unsafe_allow_html=True)

st.markdown("""
<div class="objective-card">
    <p style='font-size: 1.1rem; line-height: 1.6; color: #333333;'>
        The goal of this project is to simulate the behavior of retail and corporate clients of a Tunisian bank 
        using AI-based agent simulations. This simulation will support the geomarketing department's mission to 
        enhance the bank's attractiveness and competitiveness by modeling client responses to strategic changes 
        in products, services, geography, digital offerings, and external socio-economic factors.
    </p>
    <p style='font-size: 1.1rem; line-height: 1.6; color: #333333;'>
        Our platform provides actionable insights through three specialized modules that work together to give
        a comprehensive view of client behavior and regional distribution patterns.
    </p>
</div>
""", unsafe_allow_html=True)

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="card">
        <div class="platform-header">📊 Platform Capabilities</div>
        <p style='font-size: 1.1rem; line-height: 1.6; color: #333333;'>
            Our comprehensive banking analytics platform leverages cutting-edge AI and simulation technologies 
            to help financial institutions understand customer behavior, optimize product adoption strategies, 
            and analyze regional distribution patterns.
        </p>
        <p style='font-size: 1.1rem; line-height: 1.6; color: #333333;'>
            By combining agent-based modeling, machine learning, and interactive visualizations, we provide 
            actionable insights for banking professionals to make data-driven decisions and improve customer 
            engagement across different regions and demographics.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.image("https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80", 
             caption="Banking Analytics Dashboard")

# Application Modules Section
st.markdown('<div class="section-title">🚀 Application Modules</div>', unsafe_allow_html=True)

# Features Grid
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <h3>🤖 AI Agent System</h3>
        <p>Intelligent conversational agent for banking insights, customer support, and predictive analytics</p>
    </div>
    <div class="feature-card">
        <h3>📊 Behavior Simulator</h3>
        <p>Advanced customer behavior simulation with predictive analytics and scenario modeling</p>
    </div>
    <div class="feature-card">
        <h3>🗺️ Regional Analyst</h3>
        <p>Geographic distribution and regional performance analytics with interactive mapping</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Direct Application Links - Updated to match your actual file names
st.markdown('<div class="sub-header" style="text-align: center;">📱 Quick Access to Modules</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # Link to AI Agent (app.py)
    if st.button("🤖 AI Agent System", key="ai_agent_btn", use_container_width=True):
        st.switch_page("pages/ai_agent.py")
    st.markdown("""
    <div style='text-align: center; color: #555;'>
        Interactive AI assistant for customer insights and predictive analytics
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Link to Behavior Simulator (app2.py)
    if st.button("📊 Behavior Simulator", key="sim_btn", use_container_width=True):
        st.switch_page("pages/simulator.py")
    st.markdown("""
    <div style='text-align: center; color: #555;'>
        Client behavior modeling and scenario simulation
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Link to Regional Analyst (app3.py)
    if st.button("🗺️ Regional Analyst", key="regional_btn", use_container_width=True):
        st.switch_page("pages/distribution_map.py")
    st.markdown("""
    <div style='text-align: center; color: #555;'>
        Geographic distribution analysis and mapping
    </div>
    """, unsafe_allow_html=True)

# Benefits Section
st.markdown('<div class="section-title">💡 Key Benefits</div>', unsafe_allow_html=True)

benefits_col1, benefits_col2 = st.columns(2)

with benefits_col1:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h4 style='color: #1f77b4;'>📈 Improved Decision Making</h4>
        <p style='color: #333;'>Data-driven insights for strategic planning and resource allocation</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h4 style='color: #1f77b4;'>🎯 Enhanced Customer Experience</h4>
        <p style='color: #333;'>Personalized services based on behavioral patterns and preferences</p>
    </div>
    """, unsafe_allow_html=True)

with benefits_col2:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h4 style='color: #1f77b4;'>🌍 Regional Optimization</h4>
        <p style='color: #333;'>Targeted strategies based on geographic performance data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h4 style='color: #1f77b4;'>🔮 Predictive Capabilities</h4>
        <p style='color: #333;'>Anticipate market trends and customer needs with AI-powered forecasting</p>
    </div>
    """, unsafe_allow_html=True)

# Navigation Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80", 
             caption="Banking Analytics")
    
    st.markdown("### 📱 Navigation")
    
    # Sidebar links with proper navigation
    if st.button("🤖 AI Agent System", key="sidebar_ai", use_container_width=True):
        st.switch_page("pages/ai_agent.py")
    st.caption("Interactive AI assistant for customer insights")
    
    if st.button("📊 Behavior Simulator", key="sidebar_sim", use_container_width=True):
        st.switch_page("pages/simulator.py")
    st.caption("Client behavior modeling and scenario simulation")
    
    if st.button("🗺️ Regional Analyst", key="sidebar_regional", use_container_width=True):
        st.switch_page("pages/distribution_map.py")
    st.caption("Geographic distribution analysis and mapping")
    
    st.markdown("---")
    st.markdown("### 📞 Contact")
    st.info("""
    **Development Team:**  
    📧 contact@banking-analytics.com  
    🌐 www.banking-analytics.com
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with ❤️ using Streamlit | © 2024 Banking Analytics Suite</p>
    <p>Advanced AI-powered banking solutions for the modern financial institution</p>
</div>
""", unsafe_allow_html=True)