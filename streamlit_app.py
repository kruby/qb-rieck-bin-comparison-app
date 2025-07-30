import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Location-Based Quantity Comparison")

st.markdown("""
Upload two Excel files:
- **Customs Duty Entry List** (should contain `Item No.` and `Quantity Remaining`)
- **Bin Contents** (should contain `Item No.`, `Quantity`, and `Location Filter`)

Then select a location to compare.
""")

# File uploads
customs_file = st.file_uploader("Upload Customs Duty Entry List", type=["xlsx"])
bin_file = st.file_uploader("Upload Bin Contents", type=["xlsx"])

# Select location
location_filter = st.text_input("Enter Location to Filter (e.g., QB, RIECK):")

if customs_file and bin_file and location_filter:
    # Load data
    customs_df = pd.read_excel(customs_file, sheet_name="Customs Duty Entry List")
    bin_df = pd.read_excel(bin_file, sheet_name="Bin Contents")

    # Filter and group
    bin_filtered = bin_df[bin_df["Location Filter"] == location_filter]

    customs_grouped = customs_df.groupby("Item No.", dropna=False)["Quantity Remaining"].sum().reset_index()
    customs_grouped = customs_grouped.rename(columns={"Quantity Remaining": "Total Quantity (Customs Duty Entry List)"})

    bin_grouped = bin_filtered.groupby("Item No.", dropna=False)["Quantity"].sum().reset_index()
    bin_grouped = bin_grouped.rename(columns={"Quantity": "Total Quantity (Bin Contents)"})

    # Merge and compare
    comparison = pd.merge(customs_grouped, bin_grouped, on="Item No.", how="outer")
    comparison["Total Quantity (Customs Duty Entry List)"] = comparison["Total Quantity (Customs Duty Entry List)"].fillna(0)
    comparison["Total Quantity (Bin Contents)"] = comparison["Total Quantity (Bin Contents)"].fillna(0)
    comparison["Quantity Difference"] = (
        comparison["Total Quantity (Customs Duty Entry List)"] - comparison["Total Quantity (Bin Contents)"]
    )

    st.dataframe(comparison)

    # Prepare Excel in memory
    output = BytesIO()
    comparison.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    # Download button
    st.download_button(
        label="Download Comparison as Excel",
        data=output,
        file_name=f"Location_{location_filter}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
