import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------ PAGE SETUP ------------------------
st.set_page_config(page_title="Road Safety Cost Estimator")
st.title("Road Safety Intervention Cost Estimator")

# ------------------------ SIDEBAR ---------------------------
st.sidebar.header("Assumptions")
st.sidebar.write("""
- Material-only costs (labour, installation, taxes excluded)
- Standard sizes as per IRC clauses
- Prices from CPWD SOR 2025 / GeM portal
""")

st.sidebar.info("Steps:\n1. Upload a CSV\n2. View itemized costs\n3. Use filters & charts\n4. Download report")

# ------------------------ TOGGLES ---------------------------
compare_mode = st.checkbox("Enable Scenario Comparison (Plan A vs Plan B)")
multi_compare = st.checkbox("Enable Multi-Plan Comparison")

# ------------------------ AI FLAGS --------------------------
standard_items = [
    "Speed Breaker", "Signage", "Pedestrian Crossing", "Rumble Strip",
    "Guard Rail", "Road Marking", "Street Lighting", "Footpath"
]

def flag_intervention(row: pd.Series) -> str:
    flags = []
    # High cost
    try:
        if float(row.get("Total Cost (₹)", 0)) > 1_000_000:
            flags.append("High Cost")
    except Exception:
        pass
    # Missing IRC Code (only if present)
    if "IRC Code" in row.index:
        irc_val = row.get("IRC Code")
        if pd.isna(irc_val) or str(irc_val).strip() == "":
            flags.append("Missing IRC Code")
    # Unusual quantity
    qty = row.get("Quantity", None)
    try:
        if qty is None or float(qty) < 1 or float(qty) > 1000:
            flags.append("Unusual Quantity")
    except Exception:
        flags.append("Unusual Quantity")
    # Missing cost data
    if pd.isna(row.get("Unit Price (₹)")) or pd.isna(row.get("Total Cost (₹)")):
        flags.append("Missing Cost Data")
    # Zero cost
    try:
        if float(row.get("Total Cost (₹)", 0)) == 0:
            flags.append("Zero Cost")
    except Exception:
        pass
    # Unrecognized item
    if row.get("Intervention") not in standard_items:
        flags.append("Unrecognized Item")
    return ", ".join(flags) if flags else "OK"

# ------------------------ CHART HELPERS ---------------------
def bar_chart_with_colors(df_or_series, base_colors=None):
    if base_colors is None:
        base_colors = ["#0056b3", "#008000", "#66b3ff", "#99ff99", "#003f7f", "#00a65a"]
    if isinstance(df_or_series, pd.Series) or (isinstance(df_or_series, pd.DataFrame) and df_or_series.shape[1] == 1):
        st.bar_chart(df_or_series, color=base_colors[0])
    else:
        n_cols = df_or_series.shape[1]
        color_list = (base_colors * ((n_cols // len(base_colors)) + 1))[:n_cols]
        st.bar_chart(df_or_series, color=color_list)

def safe_pie_chart(df: pd.DataFrame):
    costs = pd.to_numeric(df["Total Cost (₹)"], errors="coerce").dropna()
    if costs.empty:
        st.warning("No valid cost data available for pie chart (missing or zero rates).")
        return
    labels = df.loc[costs.index, "Intervention"]
    fig, ax = plt.subplots()
    ax.pie(costs, labels=labels, autopct="%1.1f%%", colors=["#0056b3", "#008000", "#66b3ff", "#99ff99"])
    st.pyplot(fig)

# ------------------------ MULTI-PLAN COMPARISON -------------
if multi_compare:
    uploaded_files = st.file_uploader(
        "Upload one or more Intervention Reports (CSV)",
        type="csv",
        accept_multiple_files=True
    )

    if uploaded_files:
        # Load rates
        try:
            rates = pd.read_csv("rates.csv")
        except Exception:
            st.error("rates.csv not found or unreadable. Place rates.csv next to app.py with columns: Intervention,Unit Price (₹).")
            st.stop()

        comparison_dict = {}
        totals = []

        for file in uploaded_files:
            df = pd.read_csv(file)
            # Merge with rates
            df = df.merge(rates, on="Intervention", how="left")
            # Compute totals (numeric-safe)
            df["Total Cost (₹)"] = pd.to_numeric(df["Quantity"], errors="coerce") * pd.to_numeric(df["Unit Price (₹)"], errors="coerce")
            # AI flags
            df["AI Flag"] = df.apply(flag_intervention, axis=1)

            # Styled table
            st.subheader(f"Itemized Cost Report — {file.name}")
            styled = df.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                               .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")
            st.dataframe(styled)

            # Grand total
            total = pd.to_numeric(df["Total Cost (₹)"], errors="coerce").sum()
            totals.append({"Plan": file.name, "Total Cost (₹)": total})
            st.metric(f"Total for {file.name}", f"{total:,}")

            # Sensitivity
            variation = 0.10
            df["Cost -10%"] = df["Total Cost (₹)"] * (1 - variation)
            df["Cost +10%"] = df["Total Cost (₹)"] * (1 + variation)
            st.subheader(f"Sensitivity Analysis — {file.name} (±10%)")
            st.dataframe(df[["Intervention", "Total Cost (₹)", "Cost -10%", "Cost +10%"]])

            # Pie chart
            st.subheader(f"Cost Distribution — {file.name}")
            safe_pie_chart(df)

            # Download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(f"Download {file.name} CSV", csv, f"{file.name}_report.csv", "text/csv")

            # Comparison series per plan
            comparison_series = pd.to_numeric(df["Total Cost (₹)"], errors="coerce").groupby(df["Intervention"]).sum()
            comparison_dict[file.name] = comparison_series

        # Totals table
        totals_df = pd.DataFrame(totals)
        st.subheader("Plan totals")
        st.dataframe(totals_df)

        # Combined comparison chart
        comparison_df = pd.DataFrame(comparison_dict).fillna(0)
        st.subheader("Comparison across all uploaded plans")
        bar_chart_with_colors(comparison_df)
    else:
        st.info("Upload two or more CSV files to compare multiple plans.")

# ------------------------ PLAN A vs PLAN B -------------------
elif compare_mode:
    uploaded_file_A = st.file_uploader("Upload Intervention Report — Plan A (CSV)", type="csv", key="planA")
    uploaded_file_B = st.file_uploader("Upload Intervention Report — Plan B (CSV)", type="csv", key="planB")

    if uploaded_file_A and uploaded_file_B:
        # Load rates
        try:
            rates = pd.read_csv("rates.csv")
        except Exception:
            st.error("rates.csv not found or unreadable. Place rates.csv next to app.py with columns: Intervention,Unit Price (₹).")
            st.stop()

        # Merge and compute
        planA = pd.read_csv(uploaded_file_A).merge(rates, on="Intervention", how="left")
        planB = pd.read_csv(uploaded_file_B).merge(rates, on="Intervention", how="left")

        planA["Total Cost (₹)"] = pd.to_numeric(planA["Quantity"], errors="coerce") * pd.to_numeric(planA["Unit Price (₹)"], errors="coerce")
        planB["Total Cost (₹)"] = pd.to_numeric(planB["Quantity"], errors="coerce") * pd.to_numeric(planB["Unit Price (₹)"], errors="coerce")

        planA["AI Flag"] = planA.apply(flag_intervention, axis=1)
        planB["AI Flag"] = planB.apply(flag_intervention, axis=1)

        # Styled tables
        st.subheader("Itemized Cost Report — Plan A")
        styledA = planA.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                              .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")
        st.dataframe(styledA)
        st.metric("Plan A total (₹)", f"{pd.to_numeric(planA['Total Cost (₹)'], errors='coerce').sum():,}")

        st.subheader("Itemized Cost Report — Plan B")
        styledB = planB.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                              .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")
        st.dataframe(styledB)
        st.metric("Plan B total (₹)", f"{pd.to_numeric(planB['Total Cost (₹)'], errors='coerce').sum():,}")

        # Sensitivity
        variation = 0.10
        planA["Cost -10%"] = planA["Total Cost (₹)"] * (1 - variation)
        planA["Cost +10%"] = planA["Total Cost (₹)"] * (1 + variation)
        st.subheader("Sensitivity analysis — Plan A (±10%)")
        st.dataframe(planA[["Intervention", "Total Cost (₹)", "Cost -10%", "Cost +10%"]])

        planB["Cost -10%"] = planB["Total Cost (₹)"] * (1 - variation)
        planB["Cost +10%"] = planB["Total Cost (₹)"] * (1 + variation)
        st.subheader("Sensitivity analysis — Plan B (±10%)")
        st.dataframe(planB[["Intervention", "Total Cost (₹)", "Cost -10%", "Cost +10%"]])

        # Pie charts
        st.subheader("Cost distribution — Plan A")
        safe_pie_chart(planA)
        st.subheader("Cost distribution — Plan B")
        safe_pie_chart(planB)

        # Downloads
        csvA = planA.to_csv(index=False).encode("utf-8")
        st.download_button("Download Plan A CSV", csvA, "planA_report.csv", "text/csv")

        csvB = planB.to_csv(index=False).encode("utf-8")
        st.download_button("Download Plan B CSV", csvB, "planB_report.csv", "text/csv")

        # Comparison chart across interventions
        comparison = pd.DataFrame({
            "Plan A": pd.to_numeric(planA["Total Cost (₹)"], errors="coerce").groupby(planA["Intervention"]).sum(),
            "Plan B": pd.to_numeric(planB["Total Cost (₹)"], errors="coerce").groupby(planB["Intervention"]).sum()
        })
        st.subheader("Comparison chart — interventions by plan")
        bar_chart_with_colors(comparison, base_colors=["#0056b3", "#008000"])
    else:
        st.info("Upload both Plan A and Plan B CSV files to compare.")

# ------------------------ SINGLE PLAN -----------------------
else:
    uploaded_file = st.file_uploader("Upload Intervention Report (CSV)", type="csv")

    if uploaded_file:
        # Load rates
        try:
            rates = pd.read_csv("rates.csv")
        except Exception:
            st.error("rates.csv not found or unreadable. Place rates.csv next to app.py with columns: Intervention,Unit Price (₹).")
            st.stop()

        # Load report and merge
        report_df = pd.read_csv(uploaded_file)
        merged = report_df.merge(rates, on="Intervention", how="left")

        # Compute totals
        merged["Total Cost (₹)"] = pd.to_numeric(merged["Quantity"], errors="coerce") * pd.to_numeric(merged["Unit Price (₹)"], errors="coerce")

        # AI flags
        merged["AI Flag"] = merged.apply(flag_intervention, axis=1)

        # Intervention filter
        interventions = merged["Intervention"].unique()
        selected = st.selectbox("Filter by intervention", ["All"] + list(interventions))
        filtered = merged if selected == "All" else merged[merged["Intervention"] == selected]

        # Styled table
        st.subheader("Itemized Cost Report")
        styled = filtered.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                            .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")
        st.dataframe(styled)

        # Grand total
        total_cost = pd.to_numeric(filtered["Total Cost (₹)"], errors="coerce").sum()
        st.metric("Grand Total Estimated Cost (₹)", f"{total_cost:,}")

        # Sensitivity analysis
        variation = 0.10
        filtered["Cost -10%"] = filtered["Total Cost (₹)"] * (1 - variation)
        filtered["Cost +10%"] = filtered["Total Cost (₹)"] * (1 + variation)
        st.subheader("Sensitivity analysis (±10%)")
        st.dataframe(filtered[["Intervention", "Total Cost (₹)", "Cost -10%", "Cost +10%"]])

        # Charts
        st.subheader("Cost breakdown")
        series = pd.to_numeric(filtered.set_index("Intervention")["Total Cost (₹)"], errors="coerce").fillna(0)
        bar_chart_with_colors(series)

        st.subheader("Cost distribution")
        safe_pie_chart(filtered)

        # Download
        st.subheader("Download report")
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "cost_report.csv", "text/csv")

        # Future scope
        with st.expander("Future scope"):
            st.write("""
            - Automate CPWD/GeM scraping for live prices
            - Expand to all IRC interventions
            - Integrate with government dashboards
            - Add predictive AI for cost overruns
            - Cluster interventions by ROI or risk
            """)
    else:
        st.info("Upload a CSV file with interventions and quantities to begin.")