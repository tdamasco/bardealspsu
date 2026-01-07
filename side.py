import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
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
    .night-out-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    .route-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .ranking-slider {
        margin: 1rem 0;
    }
    .route-step {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .deal-highlight {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
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
    
    
    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]

    
    df = pd.DataFrame()
    
    for filename in possible_files:
        try:
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                
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
    """Get current day of the week in Eastern Time"""
    # Use Eastern timezone (adjust to your timezone if different)
    eastern = pytz.timezone('America/New_York')
    now_eastern = datetime.now(eastern)
    return now_eastern.strftime('%A')

def main():
    # Load data
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Header
    st.markdown('<h1 class="main-header">🍺 Bar Specials Dashboard 🍺</h1>', unsafe_allow_html=True)
    
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
        ["By Day", "By Bar", "Night Out Planner", "Summary Stats"]
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
    elif view_mode == "Night Out Planner":
        display_night_out_planner(df, selected_day if selected_day != 'All Days' else current_day)
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
                        <div>💰 {row['Deal']}</div>
                    </div>
                    """, unsafe_allow_html=True)

def display_by_bar(df, selected_bar):
    """Display specials organized by bar"""
    if selected_bar == 'All Bars':
        bars_to_show = sorted(df['Bar'].unique())
    else:
        bars_to_show = [selected_bar]
    
    for bar in bars_to_show:
        bar_data = df[df['Bar'] == bar]
        
        if not bar_data.empty:
            st.markdown(f"### 🍺 {bar}")
            
            # Display specials for each day
            for _, row in bar_data.iterrows():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**{row['Day']}**")
                with col2:
                    st.markdown(f"{row['Deal']}")
            
            st.markdown("---")

def display_summary_stats(df):
    """Display summary statistics and visualizations"""
    st.markdown("## 📊 Dashboard Statistics")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bars", df['Bar'].nunique())
    with col2:
        st.metric("Total Specials", len(df))
    with col3:
        avg_specials = len(df) / 7
        st.metric("Avg Specials/Day", f"{avg_specials:.1f}")
    with col4:
        most_active = df.groupby('Bar').size().idxmax()
        st.metric("Most Active Bar", most_active)
    
    # Visualizations
    st.markdown("### 📈 Specials Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Specials by day
        day_counts = df.groupby('Day').size().reset_index(name='Count')
        fig1 = px.bar(day_counts, x='Day', y='Count', 
                     title='Number of Specials by Day',
                     color='Count',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Specials by bar
        bar_counts = df.groupby('Bar').size().reset_index(name='Count')
        bar_counts = bar_counts.sort_values('Count', ascending=False).head(10)
        fig2 = px.bar(bar_counts, x='Bar', y='Count',
                     title='Top 10 Bars by Number of Specials',
                     color='Count',
                     color_continuous_scale='Reds')
        fig2.update_xaxis(tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Day coverage by bar
    st.markdown("### 📅 Day Coverage by Bar")
    coverage = df.groupby('Bar')['Day'].apply(list).reset_index()
    coverage['Days'] = coverage['Day'].apply(lambda x: ', '.join(sorted(set(x), key=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index)))
    coverage['Day Count'] = coverage['Day'].apply(lambda x: len(set(x)))
    coverage = coverage.sort_values('Day Count', ascending=False)
    
    st.dataframe(coverage[['Bar', 'Day Count', 'Days']], use_container_width=True)

def display_night_out_planner(df, selected_day):
    """Interactive night out planner"""
    st.markdown("## 🎉 Plan Your Night Out")
    st.markdown(f"### Planning for: **{selected_day}**")
    
    # Get bars for the selected day
    day_data = df[df['Day'] == selected_day]
    
    if day_data.empty:
        st.warning(f"No specials found for {selected_day}")
        return
    
    day_bars = day_data['Bar'].tolist()
    
    # Step 1: Rank the bars
    st.markdown("### ⭐ Step 1: Rate Your Interest")
    st.markdown("Rate each bar from 1 (not interested) to 10 (must visit)")
    
    bar_rankings = {}
    
    # Create a more compact layout for rankings
    cols = st.columns(2)
    for idx, bar in enumerate(sorted(day_bars)):
        col = cols[idx % 2]
        
        with col:
            deal = day_data[day_data['Bar'] == bar]['Deal'].iloc[0]
            st.markdown(f"**{bar}**")
            st.caption(f"Special: {deal}")
            rating = st.slider(
                "Interest level:",
                min_value=1,
                max_value=10,
                value=5,
                key=f"rating_{bar}",
                help="1 = Not interested, 10 = Must visit!"
            )
            bar_rankings[bar] = rating
            st.markdown("---")
    
    st.markdown("### ⚙️ Step 2: Customize Your Night")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_stops = st.selectbox(
            "Number of bars to visit:",
            options=[2, 3, 4, 5],
            index=1,
            help="How many bars do you want to hit?"
        )
    
    with col2:
        route_style = st.selectbox(
            "Route style:",
            options=["Optimized", "High-rated Only", "Adventure Mix"],
            help="Optimized: Best value + ratings, High-rated: Top favorites only, Adventure: Mix favorites with discoveries"
        )
    
    with col3:
        budget_conscious = st.checkbox(
            "Budget-friendly focus",
            help="Prioritize bars with better drink deals"
        )
    
    # Generate route
    if st.button("🚀 Generate My Route!", type="primary"):
        route = generate_optimal_route(
            df, selected_day, bar_rankings, num_stops, route_style, budget_conscious
        )
        
        if route:
            st.markdown("### 🎉 Your Personalized Bar Route")
            
            # Route overview
            route_bars = [stop['bar'] for stop in route]
            total_score = sum(stop['score'] for stop in route)
            avg_rating = sum(bar_rankings[bar] for bar in route_bars) / len(route_bars)
            
            st.markdown(f"""
            <div class="night-out-card">
                <h3>🍺 {selected_day} Night Out Plan</h3>
                <p><strong>Route:</strong> {' → '.join(route_bars)}</p>
                <p><strong>Total Stops:</strong> {len(route)} bars</p>
                <p><strong>Average Rating:</strong> {avg_rating:.1f}/10</p>
                <p><strong>Route Score:</strong> {total_score:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed route steps
            for idx, stop in enumerate(route, 1):
                st.markdown(f"""
                <div class="route-card">
                    <div class="route-step">Stop {idx}: {stop['bar']} 
                        <span style="float: right;">⭐ {bar_rankings[stop['bar']]}/10</span>
                    </div>
                    <div class="deal-highlight">
                        <strong>Special:</strong> {stop['deal']}
                    </div>
                    <div style="margin-top: 0.5rem;">
                        <strong>Why this stop:</strong> {stop['reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Route tips
            st.markdown("### 💡 Pro Tips for Your Night Out")
            
            tips = generate_route_tips(route, route_style, budget_conscious)
            for tip in tips:
                st.info(tip)
            
            # Alternative suggestions
            if len(day_bars) > num_stops:
                st.markdown("### 🔄 Alternative Options")
                
                remaining_bars = [bar for bar in day_bars if bar not in route_bars]
                if remaining_bars:
                    alt_bars = sorted(remaining_bars, key=lambda x: bar_rankings[x], reverse=True)[:2]
                    
                    for bar in alt_bars:
                        deal = df[(df['Day'] == selected_day) & (df['Bar'] == bar)]['Deal'].iloc[0]
                        st.markdown(f"**🔄 {bar}** (Rating: {bar_rankings[bar]}/10): {deal}")

def generate_optimal_route(df, day, rankings, num_stops, style, budget_focus):
    """Generate an optimal bar route based on preferences"""
    import random
    
    # Get available bars for the day
    day_data = df[df['Day'] == day].copy()
    
    if len(day_data) < num_stops:
        return []
    
    # Calculate scores for each bar
    bars_with_scores = []
    
    for _, row in day_data.iterrows():
        bar = row['Bar']
        deal = row['Deal']
        base_rating = rankings[bar]
        
        # Calculate deal value score (simple heuristic based on keywords)
        deal_score = calculate_deal_score(deal) if budget_focus else 5
        
        # Combine scores based on route style
        if style == "High-rated Only":
            total_score = base_rating * 1.5
        elif style == "Adventure Mix":
            # Add some randomness to encourage trying new places
            random_bonus = random.uniform(0, 2)
            total_score = base_rating + deal_score * 0.3 + random_bonus
        else:  # Optimized
            total_score = base_rating + deal_score * 0.5
        
        bars_with_scores.append({
            'bar': bar,
            'deal': deal,
            'rating': base_rating,
            'deal_score': deal_score,
            'total_score': total_score
        })
    
    # Sort by total score and select top bars
    bars_with_scores.sort(key=lambda x: x['total_score'], reverse=True)
    selected_bars = bars_with_scores[:num_stops]
    
    # Generate route with reasons
    route = []
    for i, bar_info in enumerate(selected_bars):
        reason = generate_bar_reason(bar_info, i, style, budget_focus)
        route.append({
            'bar': bar_info['bar'],
            'deal': bar_info['deal'],
            'score': bar_info['total_score'],
            'reason': reason
        })
    
    return route

def calculate_deal_score(deal_text):
    """Calculate a simple score based on deal attractiveness"""
    deal_lower = deal_text.lower()
    score = 5  # Base score
    
    # Look for price indicators
    if '$1' in deal_text or '$2' in deal_text:
        score += 3
    elif '$3' in deal_text:
        score += 2
    elif '$4' in deal_text or '$5' in deal_text:
        score += 1
    
    # Look for value keywords
    value_words = ['happy hour', 'half off', 'draft', '50 cent', 'pitcher']
    for word in value_words:
        if word in deal_lower:
            score += 1
    
    # Look for premium indicators
    premium_words = ['wine', 'cocktail', 'premium']
    for word in premium_words:
        if word in deal_lower:
            score += 0.5
    
    return min(score, 10)  # Cap at 10

def generate_bar_reason(bar_info, position, style, budget_focus):
    """Generate a reason why this bar was selected"""
    reasons = []
    
    if position == 0:
        if bar_info['rating'] >= 8:
            reasons.append("Perfect starter - one of your top-rated bars")
        else:
            reasons.append("Great way to kick off the night")
    elif position == len([]) - 1:  # This would be adjusted in real implementation
        reasons.append("Perfect finale to your night out")
    else:
        reasons.append("Excellent mid-night stop")
    
    if bar_info['rating'] >= 8:
        reasons.append(f"High personal rating ({bar_info['rating']}/10)")
    
    if budget_focus and bar_info['deal_score'] >= 7:
        reasons.append("Great drink deals")
    
    if style == "Adventure Mix" and bar_info['rating'] < 7:
        reasons.append("Good opportunity to try something new")
    
    return reasons[0] if reasons else "Solid choice for your route"

def generate_route_tips(route, style, budget_focus):
    """Generate helpful tips for the night out"""
    tips = []
    
    # General tips
    tips.append("🚗 Consider ride-sharing or designating a driver for safety")
    tips.append("💧 Stay hydrated - drink water between stops")
    
    # Style-specific tips
    if style == "High-rated Only":
        tips.append("🌟 You're hitting your favorite spots - enjoy the familiar atmosphere!")
    elif style == "Adventure Mix":
        tips.append("🎲 Great mix of favorites and new experiences - keep an open mind!")
    else:
        tips.append("⚖️ Well-balanced route optimizing both preferences and value")
    
    # Budget tips
    if budget_focus:
        tips.append("💰 Focus on the specials to maximize your budget")
        tips.append("🕒 Pay attention to happy hour times for extra savings")
    
    # Route-specific tips
    if len(route) >= 4:
        tips.append("⏰ Pace yourself - that's a lot of stops for one night!")
    
    # Deal-specific tips
    deals_text = ' '.join([stop['deal'].lower() for stop in route])
    if 'happy hour' in deals_text:
        tips.append("⏰ Plan your timing around happy hour specials")
    if 'draft' in deals_text:
        tips.append("🍺 Several draft specials - great for beer lovers!")
    
    return tips

if __name__ == "__main__":
    main()



