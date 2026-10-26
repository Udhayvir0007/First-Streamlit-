import streamlit as st
import pandas as pd
import os
import plotly.express as px  

# 1. Page Configuration & Shared Theme
st.set_page_config(
    page_title="Retail Sales Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Consistent dark template across all Plotly charts
CHART_TEMPLATE = "plotly_dark"

# 2. Data Loading Function
@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath, encoding="latin1")
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df = df.dropna(subset=['Order Date'])
    return df

# Construct path
# Use relative path so Streamlit Cloud can find it in the repo root
file_path = "ss.csv"
df = load_data(file_path)

# 3. Sidebar Interactive Filters
st.sidebar.header("🔍 Dashboard Filters")

# Region Filter
if 'Region' in df.columns:
    region_options = ["All"] + list(df['Region'].dropna().unique())
    selected_region = st.sidebar.selectbox("Select Region", region_options)
    if selected_region != "All":
        df = df[df['Region'] == selected_region]

# Category Filter
if 'Category' in df.columns:
    category_options = ["All"] + list(df['Category'].dropna().unique())
    selected_category = st.sidebar.selectbox("Select Category", category_options)
    if selected_category != "All":
        df = df[df['Category'] == selected_category]

# 4. Main Dashboard Header
st.title("📊 Retail Sales Performance Dashboard")
st.markdown("---")

# 5. Top-Level KPI Summary Cards
total_sales = df['Sales'].sum() if 'Sales' in df.columns else 0
total_profit = df['Profit'].sum() if 'Profit' in df.columns else 0
total_orders = df['Order ID'].nunique() if 'Order ID' in df.columns else len(df)
avg_order_val = (total_sales / total_orders) if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Sales ($)", value=f"${total_sales/1e6:.2f}M")
with col2:
    st.metric(label="Total Profit ($)", value=f"${total_profit/1e3:.2f}K")
with col3:
    st.metric(label="Total Orders", value=f"{total_orders:,}")
with col4:
    st.metric(label="Avg Order Value ($)", value=f"${avg_order_val:,.2f}")

st.markdown("---")

# 6. Visualizations Row 1 (Line Chart & Bar Chart)
chart_col1, chart_col2 = st.columns(2)


# Chart 1: Time-Series Line Chart
with chart_col1:
    st.subheader("Monthly Sales Trend")
    if 'Order Date' in df.columns and 'Sales' in df.columns:
        # 'ME' stands for Month End in Pandas 2.2+
        df_trend = df.resample('ME', on='Order Date')['Sales'].sum().reset_index()
        fig_line = px.line(
            df_trend, 
            x='Order Date', 
            y='Sales', 
            title="Monthly Sales Progression", 
            labels={'Sales': 'Total Revenue ($)', 'Order Date': 'Order Date'},
            template=CHART_TEMPLATE
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Columns 'Order Date' and 'Sales' are required for time-series trend.")

# Chart 2: Category Bar Chart
with chart_col2:
    st.subheader("Sales by Category")
    if 'Category' in df.columns and 'Sales' in df.columns:
        df_cat = df.groupby('Category')['Sales'].sum().reset_index()
        fig_bar = px.bar(
            df_cat, 
            x='Category', 
            y='Sales', 
            color='Category', 
            title="Sales Distribution Across Product Categories",
            labels={'Sales': 'Total Revenue ($)', 'Category': 'Product Category'},
            template=CHART_TEMPLATE
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 7. Visualizations Row 2 (Treemap & Choropleth Map)
map_col1, map_col2 = st.columns(2)

# Chart 3: Hierarchical Treemap
with map_col1:
    st.subheader("Category & Sub-Category Breakdown")
    if 'Category' in df.columns and 'Sub-Category' in df.columns and 'Sales' in df.columns:
        fig_tree = px.treemap(
            df,
            path=['Category', 'Sub-Category'],
            values='Sales',
            title="Hierarchical Category Sales Volume",
            color='Sales',
            color_continuous_scale='Viridis',
            template=CHART_TEMPLATE
        )
        st.plotly_chart(fig_tree, use_container_width=True)

# Chart 4: US Geographic Map
with map_col2:
    st.subheader("Geographic Sales Distribution")
    if 'State' in df.columns and 'Sales' in df.columns:
        df_state = df.groupby('State')['Sales'].sum().reset_index()
        fig_map = px.choropleth(
            df_state,
            locations='State',
            locationmode="USA-states",
            color='Sales',
            scope="usa",
            title="Total Sales Volume by US State",
            color_continuous_scale="Reds",
            template=CHART_TEMPLATE
        )
        st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# 8. Interactive Raw Data Display
with st.expander("📄 View Filtered Dataset"):
    st.dataframe(df)