import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Road Safety Cost Estimator")

st.title("Road Safety Intervention Cost Estimator")

# Sidebar assumptions
st.sidebar.header("Assumptions")
st.sidebar.write("""
- Material-only costs (labour, installation, taxes excluded)
- Standard sizes as per IRC clauses
- Prices from CPWD SOR 2025 / GeM portal
""")

# Sidebar mini guide
st.sidebar.info("Steps:\n1. Upload a CSV\n2. View itemized costs\n3. Use filters & charts\n4. Download report")

# Toggles
compare_mode = st.checkbox("Enable Scenario Comparison (Plan A vs Plan B)")
multi_compare = st.checkbox("Enable Multi-Plan Comparison")

# Helper for safe bar chart coloring
def bar_chart_with_colors(df_or_series, base_colors=None):
    """
    Safely render a bar chart with correct color length.
    - If a Series or single-column DataFrame, uses a single color.
    - If multi-column DataFrame, repeats/trim colors to match column count.
    """
    if base_colors is None:
        base_colors = ["#0056b3", "#008000", "#66b3ff", "#99ff99", "#003f7f", "#00a65a"]
    if isinstance(df_or_series, pd.Series) or (isinstance(df_or_series, pd.DataFrame) and df_or_series.shape[1] == 1):
        st.bar_chart(df_or_series, color=base_colors[0])
    else:
        n_cols = df_or_series.shape[1]
        color_list = (base_colors * ((n_cols // len(base_colors)) + 1))[:n_cols]
        st.bar_chart(df_or_series, color=color_list)

# ---------------- MULTI-PLAN COMPARISON ----------------
if multi_compare:
    uploaded_files = st.file_uploader(
        "Upload one or more Intervention Reports (CSV)",
        type="csv",
        accept_multiple_files=True
    )

    if uploaded_files:
        rates = pd.read_csv("rates.csv")
        comparison_dict = {}
        totals = []

        for file in uploaded_files:
            df = pd.read_csv(file)

            # Expect columns at minimum: Intervention, Quantity
            # Merge rates (must have: Intervention, Unit Price (₹))
            df = df.merge(rates, on="Intervention", how="left")

            # Compute totals
            df["Total Cost (₹)"] = df["Quantity"] * df["Unit Price (₹)"]

            # Styled table (dual-color gradients)
            styled = df.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                               .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")
            st.subheader(f"Itemized Cost Report — {file.name}")
            st.dataframe(styled)

            # Grand total
            total = df["Total Cost (₹)"].sum()
            totals.append({"Plan": file.name, "Total Cost (₹)": total})
            st.metric(f"Total for {file.name}", f"{total:,}")

            # Sensitivity analysis
            variation = 0.10
            df["Cost -10%"] = df["Total Cost (₹)"] * (1 - variation)
            df["Cost +10%"] = df["Total Cost (₹)"] * (1 + variation)
            st.subheader(f"Sensitivity Analysis — {file.name} (±10%)")
            st.dataframe(df[["Intervention", "Total Cost (₹)", "Cost -10%", "Cost +10%"]])

            # Pie chart (blue/green palette)
            st.subheader(f"Cost Distribution — {file.name}")
            fig, ax = plt.subplots()
            ax.pie(
                df["Total Cost (₹)"],
                labels=df["Intervention"],
                autopct='%1.1f%%',
                colors=["#0056b3", "#008000", "#66b3ff", "#99ff99"]
            )
            st.pyplot(fig)

            # Download button
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(f"Download {file.name} CSV", csv, f"{file.name}_report.csv", "text/csv")

            # For comparison across plans (column per file)
            comparison_dict[file.name] = df.groupby("Intervention")["Total Cost (₹)"].sum()

        # Totals table
        totals_df = pd.DataFrame(totals)
        st.subheader("Plan totals")
        st.dataframe(totals_df)

        # Combined comparison chart (one column per uploaded file)
        comparison_df = pd.DataFrame(comparison_dict).fillna(0)
        st.subheader("Comparison across all uploaded plans")
        bar_chart_with_colors(comparison_df)
    else:
        st.info("Upload two or more CSV files to compare multiple plans.")

# ---------------- PLAN A vs PLAN B ----------------
elif compare_mode:
    uploaded_file_A = st.file_uploader("Upload Intervention Report — Plan A (CSV)", type="csv", key="planA")
    uploaded_file_B = st.file_uploader("Upload Intervention Report — Plan B (CSV)", type="csv", key="planB")

    if uploaded_file_A and uploaded_file_B:
        rates = pd.read_csv("rates.csv")

        planA = pd.read_csv(uploaded_file_A).merge(rates, on="Intervention", how="left")
        planB = pd.read_csv(uploaded_file_B).merge(rates, on="Intervention", how="left")

        # Compute totals
        planA["Total Cost (₹)"] = planA["Quantity"] * planA["Unit Price (₹)"]
        planB["Total Cost (₹)"] = planB["Quantity"] * planB["Unit Price (₹)"]

        # Styled tables
        styledA = planA.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                               .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")
        styledB = planB.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                               .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")

        st.subheader("Itemized Cost Report — Plan A")
        st.dataframe(styledA)
        totalA = planA["Total Cost (₹)"].sum()
        st.metric("Plan A total (₹)", f"{totalA:,}")

        st.subheader("Itemized Cost Report — Plan B")
        st.dataframe(styledB)
        totalB = planB["Total Cost (₹)"].sum()
        st.metric("Plan B total (₹)", f"{totalB:,}")

        # Sensitivity (both plans)
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
        figA, axA = plt.subplots()
        axA.pie(
            planA["Total Cost (₹)"],
            labels=planA["Intervention"],
            autopct='%1.1f%%',
            colors=["#0056b3", "#008000", "#66b3ff", "#99ff99"]
        )
        st.pyplot(figA)

        st.subheader("Cost distribution — Plan B")
        figB, axB = plt.subplots()
        axB.pie(
            planB["Total Cost (₹)"],
            labels=planB["Intervention"],
            autopct='%1.1f%%',
            colors=["#0056b3", "#008000", "#66b3ff", "#99ff99"]
        )
        st.pyplot(figB)

        # Downloads
        csvA = planA.to_csv(index=False).encode("utf-8")
        st.download_button("Download Plan A CSV", csvA, "planA_report.csv", "text/csv")

        csvB = planB.to_csv(index=False).encode("utf-8")
        st.download_button("Download Plan B CSV", csvB, "planB_report.csv", "text/csv")

        # Comparison chart across interventions (two columns)
        comparison = pd.DataFrame({
            "Plan A": planA.groupby("Intervention")["Total Cost (₹)"].sum(),
            "Plan B": planB.groupby("Intervention")["Total Cost (₹)"].sum()
        })
        st.subheader("Comparison chart — interventions by plan")
        bar_chart_with_colors(comparison, base_colors=["#0056b3", "#008000"])
    else:
        st.info("Upload both Plan A and Plan B CSV files to compare.")

# ---------------- SINGLE PLAN ----------------
else:
    uploaded_file = st.file_uploader("Upload Intervention Report (CSV)", type="csv")

    if uploaded_file:
        rates = pd.read_csv("rates.csv")
        report_df = pd.read_csv(uploaded_file)

        # Merge rates (must have: Intervention, Unit Price (₹))
        merged = report_df.merge(rates, on="Intervention", how="left")

        # Compute totals
        merged["Total Cost (₹)"] = merged["Quantity"] * merged["Unit Price (₹)"]

        # Intervention filter
        interventions = merged["Intervention"].unique()
        selected = st.selectbox("Filter by intervention", ["All"] + list(interventions))
        filtered = merged if selected == "All" else merged[merged["Intervention"] == selected]

        # Styled table (dual-color gradients)
        styled = filtered.style.background_gradient(subset=["Quantity"], cmap="Blues") \
                               .background_gradient(subset=["Total Cost (₹)"], cmap="Greens")
        st.subheader("Itemized Cost Report")
        st.dataframe(styled)

        # Grand total
        st.metric("Grand Total Estimated Cost (₹)", f"{filtered['Total Cost (₹)'].sum():,}")

        # Sensitivity analysis
        variation = 0.10
        filtered["Cost -10%"] = filtered["Total Cost (₹)"] * (1 - variation)
        filtered["Cost +10%"] = filtered["Total Cost (₹)"] * (1 + variation)
        st.subheader("Sensitivity analysis (±10%)")
        st.dataframe(filtered[["Intervention", "Total Cost (₹)", "Cost -10%", "Cost +10%"]])

        # Charts
        st.subheader("Cost breakdown")
        series = filtered.set_index("Intervention")["Total Cost (₹)"]
        bar_chart_with_colors(series)

        st.subheader("Cost distribution")
        fig, ax = plt.subplots()
        ax.pie(
            filtered["Total Cost (₹)"],
            labels=filtered["Intervention"],
            autopct='%1.1f%%',
            colors=["#0056b3", "#008000", "#66b3ff", "#99ff99"]
        )
        st.pyplot(fig)

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
            """)
    else:
        st.info("Upload a CSV file with interventions and quantities to begin.")