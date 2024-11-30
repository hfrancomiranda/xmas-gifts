import streamlit as st
import pandas as pd

# Initialize session state for storing data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Recipient", "Gift", "Budget", "Cost", "Purchased", "Gift Link"])

# Title
st.title("🎄 Christmas Gift Tracker")

# Input form for adding a gift
st.header("Add a Gift")
with st.form("add_gift_form"):
    recipient = st.text_input("Recipient Name")
    gift = st.text_input("Gift Idea")
    budget = st.number_input("Budget", min_value=0.0, step=1.0)
    cost = st.number_input("Actual Cost (if purchased)", min_value=0.0, step=1.0, value=0.0)
    purchased = st.selectbox("Purchased?", ["No", "Yes"])
    link = st.text_input("Gift Link (URL)", placeholder="e.g., https://example.com/gift")
    submitted = st.form_submit_button("Add Gift")

    if submitted:
        new_entry = {
            "Recipient": recipient,
            "Gift": gift,
            "Budget": budget,
            "Cost": cost,
            "Purchased": purchased,
            "Gift Link": link
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
        st.success("Gift added successfully!")

# Display and manage the gift list
st.header("Gift List")
if not st.session_state.data.empty:
    # Make links clickable directly in the DataFrame
    st.session_state.data["Gift Link"] = st.session_state.data["Gift Link"].apply(
        lambda x: f'<a href="{x}" target="_blank">{x}</a>' if pd.notna(x) and x != "" else ""
    )

    # Editable DataFrame
    edited_data = st.data_editor(
        st.session_state.data,
        num_rows="dynamic",
        use_container_width=True,
        disabled=["Gift Link"]  # Prevent editing links directly to avoid formatting issues
    )

    # Update the session state with edited data
    st.session_state.data = edited_data

# Budget Summary
if not st.session_state.data.empty:
    st.header("Budget Summary")
    total_budget = st.session_state.data["Budget"].sum()
    total_spent = st.session_state.data[st.session_state.data["Purchased"] == "Yes"]["Cost"].sum()
    remaining_budget = total_budget - total_spent
    st.metric("Total Budget", f"${total_budget:.2f}")
    st.metric("Total Spent", f"${total_spent:.2f}")
    st.metric("Remaining Budget", f"${remaining_budget:.2f}")

# Save data to a file
st.subheader("Download the Gift List")
csv_data = st.session_state.data.to_csv(index=False)
st.download_button("Download as CSV", csv_data, "christmas_gift_list.csv", "text/csv")
