import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Bar Specials Dashboard",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B35;
        margin-bottom: 2rem;
    }
    .day-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
        margin: 1rem 0;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.5rem;
    }
    .bar-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .bar-name {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .deal-text {
        font-size: 1rem;
        line-height: 1.4;
    }
    .sidebar-content {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the bar specials data"""
    import os
    
    # Try different possible file names
    possible_files = [
        'joined_specials 1.csv',
        'joined_specials_1.csv',
        'joined_specials.csv',
        'bar_specials.csv'
    ]
    
    current_dir = os.getcwd()
    st.sidebar.info(f"Looking for CSV file in: {current_dir}")
    
    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
    if csv_files:
        st.sidebar.info(f"CSV files found: {', '.join(csv_files)}")
    
    df = pd.DataFrame()
    
    for filename in possible_files:
        try:
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                st.sidebar.success(f"✅ Loaded data from: {filename}")
                break
        except Exception as e:
            st.sidebar.error(f"Error loading {filename}: {str(e)}")
            continue
    
    if df.empty:
        st.error(f"""
        ❌ **CSV file not found!**
        
        **Please follow these steps:**
        1. Make sure your CSV file is in the same directory as this Python script
        2. The file should be named one of: {', '.join(possible_files)}
        3. Current directory: `{current_dir}`
        4. CSV files in directory: {csv_files if csv_files else 'None found'}
        
        **To fix this:**
        - Copy `joined_specials 1.csv` to the same folder as your `app.py` file
        - Or rename your CSV file to match one of the expected names above
        """)
        return pd.DataFrame()
    
    # Clean any whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Verify required columns exist
    required_columns = ['Bar', 'Day', 'Deal']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}. Found columns: {list(df.columns)}")
        return pd.DataFrame()
    
    # Define day order for proper sorting
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['Day'] = pd.Categorical(df['Day'], categories=day_order, ordered=True)
    
    return df.sort_values(['Day', 'Bar'])

def get_current_day():
    """Get current day of the week"""
    return datetime.now().strftime('%A')

def main():
    # Load data
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Header
    st.markdown('<h1 class="main-header">🍺 PSU BAR DEALS 🍺</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.sidebar.header("🔍 Filters & Options")
    
    # Current day highlight
    current_day = get_current_day()
    st.sidebar.success(f"Today is {current_day}!")
    
    # Day filter
    days = ['All Days'] + list(df['Day'].cat.categories)
    selected_day = st.sidebar.selectbox(
        "Select Day:",
        days,
        index=days.index(current_day) if current_day in days else 0
    )
    
    # Bar filter
    bars = ['All Bars'] + sorted(df['Bar'].unique().tolist())
    selected_bar = st.sidebar.selectbox("Select Bar:", bars)
    
    # View mode
    view_mode = st.sidebar.radio(
        "View Mode:",
        ["By Day", "By Bar", "Summary Stats"]
    )
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Filter data based on selections
    filtered_df = df.copy()
    if selected_day != 'All Days':
        filtered_df = filtered_df[filtered_df['Day'] == selected_day]
    if selected_bar != 'All Bars':
        filtered_df = filtered_df[filtered_df['Bar'] == selected_bar]
    
    # Main content based on view mode
    if view_mode == "By Day":
        display_by_day(filtered_df, selected_day)
    elif view_mode == "By Bar":
        display_by_bar(filtered_df, selected_bar)
    else:
        display_summary_stats(df)

def display_by_day(df, selected_day):
    """Display specials organized by day"""
    if selected_day == 'All Days':
        days_to_show = df['Day'].cat.categories
    else:
        days_to_show = [selected_day]
    
    for day in days_to_show:
        day_data = df[df['Day'] == day]
        
        if not day_data.empty:
            # Day header with emoji
            day_emoji = {
                'Monday': '🏁', 'Tuesday': '🔥', 'Wednesday': '🐪', 
                'Thursday': '⚡', 'Friday': '🎉', 'Saturday': '🌟', 'Sunday': '😴'
            }
            
            st.markdown(f'<h2 class="day-header">{day_emoji.get(day, "📅")} {day} Specials</h2>', 
                       unsafe_allow_html=True)
            
            # Create columns for better layout
            cols = st.columns(2)
            
            for idx, (_, row) in enumerate(day_data.iterrows()):
                col = cols[idx % 2]
                
                with col:
                    st.markdown(f"""
                    <div class="bar-card">
                        <div class="bar-name">🍻 {row['Bar']}</div>
                        <div class="deal-text">{row['Deal']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")

def display_by_bar(df, selected_bar):
    """Display specials organized by bar"""
    if selected_bar == 'All Bars':
        bars_to_show = sorted(df['Bar'].unique())
    else:
        bars_to_show = [selected_bar]
    
    for bar in bars_to_show:
        bar_data = df[df['Bar'] == bar].sort_values('Day')
        
        if not bar_data.empty:
            st.markdown(f'<h2 class="day-header">🏪 {bar}</h2>', unsafe_allow_html=True)
            
            # Create a more compact layout for bar view
            for _, row in bar_data.iterrows():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**{row['Day']}**")
                
                with col2:
                    st.markdown(f"🍺 {row['Deal']}")
            
            st.markdown("---")

def display_summary_stats(df):
    """Display summary statistics and visualizations"""
    st.markdown('<h2 class="day-header">📊 Summary Statistics</h2>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bars", df['Bar'].nunique())
    
    with col2:
        st.metric("Total Specials", len(df))
    
    with col3:
        st.metric("Days Covered", df['Day'].nunique())
    
    with col4:
        avg_specials = len(df) / df['Bar'].nunique()
        st.metric("Avg Specials/Bar", f"{avg_specials:.1f}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart of specials by day
        day_counts = df.groupby('Day').size().reset_index(name='Count')
        fig1 = px.bar(
            day_counts, 
            x='Day', 
            y='Count',
            title='Number of Specials by Day',
            color='Count',
            color_continuous_scale='viridis'
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Bar chart of specials by bar
        bar_counts = df.groupby('Bar').size().reset_index(name='Count')
        fig2 = px.bar(
            bar_counts, 
            x='Bar', 
            y='Count',
            title='Number of Specials by Bar',
            color='Count',
            color_continuous_scale='plasma'
        )
        fig2.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed breakdown table
    st.markdown("### 📋 Detailed Breakdown")
    
    # Create a pivot table showing which bars have specials on which days
    pivot_table = df.pivot_table(
        index='Bar', 
        columns='Day', 
        values='Deal', 
        aggfunc='first',
        fill_value=''
    )
    
    # Style the dataframe
    def highlight_cells(val):
        return 'background-color: lightgreen' if val != '' else ''
    
    styled_table = pivot_table.style.applymap(highlight_cells)
    st.dataframe(styled_table, use_container_width=True)
    
    # Raw data table
    with st.expander("🔍 View Raw Data"):
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
