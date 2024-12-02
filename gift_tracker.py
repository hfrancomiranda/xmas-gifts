import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# Streamlit Page Configuration
st.set_page_config(page_title="Gift Tracker", layout="wide")

# Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Load the CSV into a DataFrame
    df = pd.read_csv(uploaded_file)
    
    # Ensure necessary columns exist
    required_columns = {"Recipient Name", "Gift Idea", "Cost", "Purchased?", "Gift Link"}
    if not required_columns.issubset(df.columns):
        st.error("The uploaded CSV must include the following columns: Recipient Name, Gift Idea, Cost, Purchased?, Gift Link")
    else:
        # Create a mutable copy for updates
        updated_df = df.copy()

        # Display the Gift List with Update Options
        st.header("Gift List with Update Options")

        # Group the DataFrame by Recipient Name and sort within each group by Cost (descending)
        grouped = (
            updated_df.groupby("Recipient Name", group_keys=False)
            .apply(lambda x: x.sort_values(by="Cost", ascending=False))
        )

        # Display grouped data with column headers and expandable sections
        for recipient_name, group in grouped.groupby("Recipient Name"):
            with st.expander(f"Recipient: {recipient_name}", expanded=False):  # Default collapsed
                # Add column headers inside each section
                col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 3])
                with col1:
                    st.markdown("**Gift Idea**")
                with col2:
                    st.markdown("**Cost**")
                with col3:
                    st.markdown("**Purchased?**")
                with col4:
                    st.markdown("**Gift Link**")

                # Display data rows
                for index, row in group.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 3])
                    with col1:
                        st.text(row["Gift Idea"])
                    with col2:
                        st.text(f"${int(row['Cost']):,}")  # Round and format cost
                    with col3:
                        updated_df.at[index, "Purchased?"] = st.radio(
                            "Purchased?",
                            options=["No", "Yes"],
                            index=["No", "Yes"].index(row["Purchased?"]),
                            key=f"purchase_{index}",
                        )
                    with col4:
                        st.markdown(f"[Link]({row['Gift Link']})", unsafe_allow_html=True)

        # Display the updated DataFrame
        st.subheader("Updated Gift List")
        st.dataframe(updated_df, use_container_width=True)

        # Add Budget Summary
        st.subheader("Budget Summary by Recipient")

        # Ensure the "Cost" column is numeric
        updated_df["Cost"] = pd.to_numeric(updated_df["Cost"], errors="coerce")

        # Default budget for each recipient
        budget = 300

        # Create Waterfall Charts for purchased items
        st.subheader("Waterfall Charts for Purchased Items")
        for recipient, group in updated_df.groupby("Recipient Name"):
            # Filter for purchased items
            purchased_items = group[group["Purchased?"] == "Yes"]

            if not purchased_items.empty:
                purchased_cost = purchased_items["Cost"].sum()
                remaining = budget - purchased_cost

                # Prepare data for the chart
                chart_data = pd.DataFrame({
                    "Gift Idea": list(purchased_items["Gift Idea"]) + ["Remaining"],
                    "Cost": list(purchased_items["Cost"]) + [remaining]
                })

                # Create the chart
                fig, ax = plt.subplots(figsize=(8, 5))
                values = chart_data["Cost"].round(0).astype(int)  # Round and convert to integer
                labels = chart_data["Gift Idea"]
                bar_colors = ['green' if x != "Remaining" else 'blue' for x in labels]
                bars = ax.bar(range(len(values)), values, color=bar_colors)

                # Identify the index of the highest value
                max_index = values.idxmax()

                # Annotate bars
                for i, bar in enumerate(bars):
                    if i == max_index:
                        # Label inside the bar for the highest amount
                        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                                f"${values[i]:,}", ha='center', va='center', color='white', fontsize=10)
                    else:
                        # Label at the top for other bars
                        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                                f"${values[i]:,}", ha='center', va='bottom', fontsize=10)

                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=45, ha='right')
                ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
                ax.set_title(f"Waterfall Chart for {recipient}")
                ax.set_ylabel("Cost ($)")
                ax.set_xlabel("Gift Ideas")
                plt.tight_layout()

                # Render the chart in Streamlit
                st.pyplot(fig)

        # Button to save data to PostgreSQL
        if st.button("Save to Database"):
            # Database connection configuration
            db_config = {
                "user": "postgres",
                "password": "3443",
                "host": "localhost",
                "port": "5432",
                "database": "finances"
            }
            connection_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

            try:
                # Save to database
                engine = create_engine(connection_string)
                updated_df.to_sql("gift_tracker", engine, if_exists="replace", index=False)
                st.success("Data saved to database successfully!")
            except Exception as e:
                st.error(f"Error saving to database: {e}")
