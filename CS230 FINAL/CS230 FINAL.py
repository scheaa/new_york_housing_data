"""
Name: Socheata Chea
CS230: Section 2
Data: New York Housing Market
URL: (link to Streamlit Cloud if deployed)
Description: This program explores NY housing listings using visual charts, filters, and maps.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# --- Load Data with Error Checking ---
# reads the data and removes row with missing values
#Filters out rows with prices ≤ 0
#Shows an error in the app if the file can't be read
def read_data():
    try:
        df = pd.read_csv("NY-House-Dataset.csv")
        df = df.dropna(subset=['PRICE', 'BEDS', 'BATH', 'PROPERTYSQFT', 'LATITUDE', 'LONGITUDE'])
        df = df[df['PRICE'] > 0]
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

# --- Filter Top 10% Expensive ---
def filter_top_10_percent(df):
    threshold = df['PRICE'].quantile(0.90)
    return df[df['PRICE'] >= threshold]

# --- Filter Top 10% Cheapest ---
def filter_bottom_10_percent(df):
    threshold = df['PRICE'].quantile(0.10)
    return df[df['PRICE'] <= threshold]

# --- Custom Filter Function ---
#Filters the dataframe by: Minimum number of beds, Minimum number of baths, Minimum square footage
def custom_filter(df, beds, baths, sqft_min=0):
    return df[(df['BEDS'] >= beds) & (df['BATH'] >= baths) & (df['PROPERTYSQFT'] >= sqft_min)]

# --- Return Multiple Stats ---
#Returns three values: Minimum price, Maximum price, Average price
def get_price_stats(df):
    return df['PRICE'].min(), df['PRICE'].max(), df['PRICE'].mean()

selected_tab = st.sidebar.radio("Navigation", ["📈Market Overview", "🔍Explore Listings", "🏠Property Types",
                                               "🏷️Price Estimator"])

# --- Main App ---
def main():
    st.image("360_F_178909435_yQyvE8unXJMdu0v4WnH6OK6EFrlMHHj5.jpg")
    st.title("New York Housing Market Explorer")
    df = read_data()

    # --- Top 10% Expensive ---
    #Generate a pivot table that shows average price by property type and borough (SUBLOCALITY)
    if selected_tab == "📈Market Overview":
        st.subheader("📊 Pivot Table: Avg Price by Property Type and Sub-Locality")
        pivot_table = df.pivot_table(
            index='SUBLOCALITY',
            columns='TYPE',
            values='PRICE',
            aggfunc='mean'
        )
        st.dataframe(pivot_table.style.format("${:,.0f}"))
        top10_df = filter_top_10_percent(df)
        if len(top10_df) > 0:
            st.header("Top 10% Most Expensive Properties")
            st.dataframe(top10_df[['ADDRESS', 'PRICE', 'TYPE', 'BEDS', 'BATH']])
            #If data exists, it shows a table with address, price, type, beds, and baths.

            counts = top10_df['TYPE'].value_counts()
            total = counts.sum()
            labels = [f"{t} ({c} | {c / total:.1%})" for t, c in counts.items()]
            #How many properties of each type exist in the bottom 10%
            #Creates custom labels showing both the count and the percent

            fig1, ax1 = plt.subplots(figsize=(10, 10))
            wedges, texts, autotexts = ax1.pie(counts, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 12})
            ax1.set_title("Property Type Distribution (Top 10% Expensive)", fontsize=14)
            ax1.legend(wedges, labels, title="Property Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                       fontsize=10)
            st.pyplot(fig1)
        else:
            st.warning("No data found for top 10% most expensive properties.")

        # --- Top 10% Cheapest ---
        st.header("Top 10% Least Expensive Properties")
        bottom10_df = filter_bottom_10_percent(df)

        if len(bottom10_df) > 0:
            st.dataframe(bottom10_df[['ADDRESS', 'PRICE', 'TYPE', 'BEDS', 'BATH']])

            counts = bottom10_df['TYPE'].value_counts()
            total = counts.sum()
            labels = [f"{t} ({c} | {c / total:.1%})" for t, c in counts.items()]

            fig2, ax2 = plt.subplots(figsize=(10, 10))
            wedges, texts, autotexts = ax2.pie(counts, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 12})
            ax2.set_title("Property Type Distribution (Top 10% Cheapest)", fontsize=14)
            ax2.legend(wedges, labels, title="Property Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                       fontsize=10)
            st.pyplot(fig2)
        else:
            st.warning("No data found for top 10% least expensive properties.")

# --- Isolated Sidebar: Sort by Price and Sub-Locality ---
    if selected_tab == "🔍Explore Listings":
        st.header("📍Explore Listing by Location")
        st.sidebar.expander("Sort by Price & Sub-Locality", expanded=False)
        selected_area = st.selectbox("Choose a Sub-Locality:", sorted(df['SUBLOCALITY'].dropna().unique()), key='sublocality')
        sorted_df = df[df['SUBLOCALITY'] == selected_area].sort_values(by='PRICE', ascending=False)
        st.subheader(f"Sorted Listings in {selected_area}")

        if len(sorted_df) > 0:
            st.dataframe(sorted_df[['ADDRESS', 'PRICE', 'TYPE', 'BEDS', 'BATH']])

            avg_price = sorted_df.groupby('TYPE')['PRICE'].mean()
            fig3, ax3 = plt.subplots()
            ax3.bar(avg_price.index, avg_price.values, edgecolor='black')
            ax3.set_title(f"Avg Price by Property Type in {selected_area}")
            ax3.set_ylabel("Avg Price ($)")
            ax3.set_xticks(range(len(avg_price)))
            ax3.set_xticklabels(avg_price.index, rotation=45, ha='right')
            st.pyplot(fig3)
            #rotation - tilts axis labels for readability
            #edgecolor - outline each bar black
        else:
            st.warning(f"No listings found for {selected_area}.")

    # --- Isolated Sidebar: Beds & Baths ---
    if selected_tab == "🏠Property Types":
        st.header("Filter by Beds and Baths")
        bed = st.selectbox("🛏️Minimum Bedrooms", sorted(df['BEDS'].dropna().unique()), key='beds')
        bath = st.selectbox("🚿Minimum Bathrooms", sorted(df['BATH'].dropna().unique()), key='baths')
        filtered_df = custom_filter(df, bed, bath)
        #Use custom_filter() to return matching listings
        st.subheader("Filtered by Bedrooms & Bathrooms")
        if len(filtered_df) > 0:
            st.dataframe(filtered_df[['ADDRESS', 'PRICE', 'BEDS', 'BATH']])

            fig4, ax4 = plt.subplots()
            fig4, ax4 = plt.subplots()
            ax4.scatter(filtered_df['BEDS'], filtered_df['PRICE'], color='dodgerblue', edgecolor='black', alpha=0.7)
            ax4.set_title("Scatterplot: Bedrooms vs. Price")
            ax4.set_xlabel("Number of Bedrooms")
            ax4.set_ylabel("Price ($)")
            st.pyplot(fig4)
        else:
            st.warning("No listings match the selected beds/baths criteria.")

    # --- Isolated Sidebar: Sqft and Location ---
    if selected_tab =="🏷️Price Estimator":
        st.header("Filter by Sqft & Location")
        location = st.selectbox("📍Select a Borough:", sorted(df['SUBLOCALITY'].dropna().unique()), key='borough')
        sqft = st.slider("📏Min Property Sqft", 0, int(df['PROPERTYSQFT'].max()), 1000, key='sqft')
        subset = df[(df['SUBLOCALITY'] == location) & (df['PROPERTYSQFT'] >= sqft)]
        st.subheader(f"Listings in {location} with Sqft ≥ {sqft}")

        if len(subset) > 0:
            st.dataframe(subset[['ADDRESS', 'PROPERTYSQFT', 'PRICE', 'BEDS', 'BATH']])

            view_state = pdk.ViewState(
                latitude=subset['LATITUDE'].mean(),
                longitude=subset['LONGITUDE'].mean(),
                zoom=11,
                pitch=0
            )

            layer = pdk.Layer(
                'ScatterplotLayer',
                data=subset,
                pickable=True,
                get_position='[LONGITUDE, LATITUDE]',
                get_radius=100,
                get_color='[200, 30, 0, 160]',  # Red semi-transparent
                radius_scale=1,
                radius_min_pixels=5,
                radius_max_pixels=15,
            )

            tooltip = {
                "html": (
                    "<b>Address:</b> {ADDRESS}<br/>"
                    "<b>Price:</b> ${PRICE}<br/>"
                    "<b>Beds:</b> {BEDS}<br/>"
                    "<b>Baths:</b> {BATH}<br/>"
                    "<b>Sqft:</b> {PROPERTYSQFT}"
                ),
                "style": {
                    "backgroundColor": "black",
                    "color": "white"
                }
            }

            deck = pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=view_state,
                layers=[layer],
                tooltip=tooltip
            )

            st.pydeck_chart(deck)

            stats = get_price_stats(subset)
            st.markdown(f"**Min Price:** ${int(stats[0]):,}  ")
            st.markdown(f"**Max Price:** ${int(stats[1]):,}  ")
            st.markdown(f"**Avg Price:** ${int(stats[2]):,}")
        else:
            st.warning("No listings match the selected sqft and location criteria.")

if __name__ == "__main__":
    main()

