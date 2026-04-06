import os

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="AI Program Risk Intelligence", layout="wide")

RISK_COLORS = {
    "HIGH": "#ef4444",
    "MEDIUM": "#f59e0b",
    "LOW": "#38bdf8",
}

READINESS_COLORS = {
    "GO": "#22c55e",
    "GO_WITH_RISKS": "#f59e0b",
    "NO_GO": "#ef4444",
}

RISK_TYPE_COLORS = {
    "Delivery Execution": "#8b5cf6",
    "Operational": "#06b6d4",
    "Dependency": "#f97316",
    "Quality": "#ec4899",
    "Security": "#ef4444",
    "Compliance": "#14b8a6",
    "Schedule": "#facc15",
    "Stakeholder Alignment": "#84cc16",
    "Scope / Change": "#a855f7",
}

OWNER_PALETTE = [
    "#60a5fa",
    "#34d399",
    "#f59e0b",
    "#f472b6",
    "#a78bfa",
    "#22d3ee",
    "#fb7185",
    "#facc15",
]


def get_latest_csv():
    files = [name for name in os.listdir() if name.startswith("results_") and name.endswith(".csv")]
    if not files:
        return None
    files.sort(key=lambda name: os.path.getmtime(name), reverse=True)
    return files[0]


def load_data():
    latest = get_latest_csv()
    if not latest:
        return None, pd.DataFrame()

    df = pd.read_csv(latest)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return latest, df


def inject_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(37, 99, 235, 0.18), transparent 24%),
                radial-gradient(circle at top left, rgba(16, 185, 129, 0.12), transparent 20%),
                linear-gradient(180deg, #0b1220 0%, #101827 100%);
            color: #e5eefc;
        }
        h1, h2, h3, h4, h5, h6, label, p, span, div {
            color: #e5eefc;
        }
        .hero-card, .panel-card, .summary-card, .action-card, .detail-card {
            background: rgba(15, 23, 42, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(2, 6, 23, 0.20);
        }
        .hero-card, .panel-card, .summary-card, .action-card, .detail-card {
            padding: 18px;
        }
        .hero-card {
            margin-bottom: 16px;
        }
        .summary-card, .action-card, .detail-card {
            min-height: 100%;
        }
        .muted {
            color: #b9c5d8 !important;
        }
        .hero-badge, .chip {
            display: inline-block;
            padding: 5px 11px;
            border-radius: 999px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 0.82rem;
            background: rgba(59, 130, 246, 0.18);
            color: #dbeafe !important;
        }
        .risk-chip-high {
            background: rgba(239, 68, 68, 0.18);
            color: #fecaca !important;
        }
        .risk-chip-medium {
            background: rgba(245, 158, 11, 0.18);
            color: #fde68a !important;
        }
        .risk-chip-low {
            background: rgba(56, 189, 248, 0.18);
            color: #bae6fd !important;
        }
        .ready-go {
            color: #86efac !important;
        }
        .ready-go_with_risks {
            color: #fde68a !important;
        }
        .ready-no_go {
            color: #fca5a5 !important;
        }
        .kicker {
            font-size: 0.9rem;
            color: #b9c5d8 !important;
        }
        .big-value {
            font-size: 2.1rem;
            font-weight: 700;
            margin-top: 8px;
        }
        div[data-baseweb="select"] > div {
            background: #f8fafc !important;
            color: #0f172a !important;
            border-radius: 12px !important;
            border: 1px solid #cbd5e1 !important;
            min-height: 46px !important;
        }
        div[data-baseweb="select"] > div * {
            color: #0f172a !important;
            fill: #0f172a !important;
        }
        div[data-baseweb="select"] input::placeholder {
            color: #475569 !important;
            -webkit-text-fill-color: #475569 !important;
            opacity: 1 !important;
        }
        div[data-baseweb="popover"] * {
            color: #0f172a !important;
        }
        div[role="listbox"] {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
        }
        div[role="option"] {
            background: #ffffff !important;
            color: #0f172a !important;
        }
        div[role="option"] * {
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            opacity: 1 !important;
        }
        div[role="option"]:hover {
            background: #dbeafe !important;
        }
        .stSelectbox label {
            color: #dbe7f7 !important;
            font-weight: 600 !important;
        }
        .stDownloadButton button {
            background: #e2e8f0 !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            font-weight: 600 !important;
        }
        .stDownloadButton button * {
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            opacity: 1 !important;
        }
        .stDownloadButton button:hover {
            background: #cbd5e1 !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
        }
        .streamlit-expanderHeader {
            color: #0f172a !important;
            background: #e2e8f0 !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
        }
        .streamlit-expanderContent {
            background: rgba(15, 23, 42, 0.82) !important;
            color: #e5eefc !important;
            border-radius: 0 0 12px 12px !important;
        }
        .streamlit-expanderContent * {
            color: #e5eefc !important;
        }
        .streamlit-expanderHeader svg {
            fill: #0f172a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def readiness_chip(status):
    color = READINESS_COLORS.get(str(status).upper(), "#94a3b8")
    return f'<span class="chip" style="background:{color}22; color:{color} !important;">Readiness: {status}</span>'


def risk_chip(risk_level):
    risk_level = str(risk_level).upper()
    css = f"risk-chip-{risk_level.lower()}"
    return f'<span class="chip {css}">Risk: {risk_level}</span>'


def build_bar_chart(dataframe, x, y, color=None, color_map=None):
    fig = px.bar(
        dataframe,
        x=x,
        y=y,
        color=color,
        color_discrete_map=color_map,
        text_auto=True,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.55)",
        font={"color": "#e5eefc"},
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        showlegend=bool(color),
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.10)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.10)")
    return fig


def build_dynamic_color_map(values, palette):
    unique_values = [str(value) for value in values if pd.notna(value)]
    return {value: palette[idx % len(palette)] for idx, value in enumerate(unique_values)}


def render_summary_card(title, value, detail, color):
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="kicker">{title}</div>
            <div class="big-value" style="color:{color};">{value}</div>
            <div class="muted" style="margin-top:8px;">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_readiness_status(value):
    return str(value).replace("_", " ")


def display_issue_title(row):
    issue_title = str(row.get("issue_title", "")).strip()
    sub_risk = str(row.get("sub_risk_type", "")).strip()
    risk_type = str(row.get("risk_type", "")).strip()
    milestone = str(row.get("milestone", "")).strip()

    if issue_title:
        return issue_title
    if sub_risk:
        return sub_risk
    if risk_type and milestone:
        return f"{risk_type} | {milestone}"
    return str(row.get("project_name", "Program Issue")).strip()


def render_action_card(row):
    risk_level = str(row["risk_level"]).upper()
    readiness = row.get("release_readiness_status", "GO_WITH_RISKS")
    blocker_label = "Top blocker" if str(row.get("blocking_flag", "No")).strip().lower() == "yes" else "Priority issue"
    st.markdown(
        f"""
        <div class="action-card">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
                <div>
                    <h3 style="margin:0;">{display_issue_title(row)}</h3>
                    <div class="muted" style="margin-top:4px;">{row['risk_type']} | {row['milestone']}</div>
                </div>
                <div>{readiness_chip(format_readiness_status(readiness))} {risk_chip(risk_level)}</div>
            </div>
            <div style="margin-top:14px;">
                <p><strong>{blocker_label}:</strong> {row['root_cause']}</p>
                <p><strong>Immediate action:</strong> {row['recommended_action']}</p>
                <p><strong>Owner:</strong> {row['action_owner']} | <strong>Urgency:</strong> {row['urgency']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_detail_card(row):
    risk_level = str(row["risk_level"]).upper()
    readiness = row.get("release_readiness_status", "GO_WITH_RISKS")
    st.markdown(
        f"""
        <div class="detail-card">
            <div style="display:flex; justify-content:space-between; gap:16px; align-items:flex-start; flex-wrap:wrap;">
                <div>
                    <h3 style="margin:0; color:#f8fbff;">{display_issue_title(row)}</h3>
                    <div class="muted" style="margin-top:6px;">{row['risk_type']} | {row['milestone']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.5rem; font-weight:700; color:{RISK_COLORS.get(risk_level, '#dbeafe')};">{risk_level}</div>
                    <div class="muted">Score {row['risk_score']}/100 | Confidence {row['confidence_score']}/100</div>
                </div>
            </div>
            <div style="margin-top:14px;">
                {readiness_chip(format_readiness_status(readiness))}
                {risk_chip(risk_level)}
                <span class="chip">Blocking: {row.get('blocking_flag', 'No')}</span>
                <span class="chip">Subtype: {row.get('sub_risk_type', 'General')}</span>
                <span class="chip">Urgency: {row['urgency']}</span>
            </div>
            <div style="margin-top:16px;">
                <p><strong>Root cause:</strong> {row['root_cause']}</p>
                <p><strong>Business impact:</strong> {row['business_impact']}</p>
                <p><strong>Recommended action:</strong> {row['recommended_action']}</p>
                <p><strong>Owner:</strong> {row['action_owner']}</p>
                <p><strong>Explanation:</strong> {row['explanation']}</p>
                <p><strong>Evidence:</strong> {row['evidence_signals']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

st.markdown(
    """
    <div class="hero-card">
        <span class="hero-badge">Executive-ready</span>
        <span class="hero-badge">AI-assisted</span>
        <span class="hero-badge">Explainable</span>
        <span class="hero-badge">Action-oriented</span>
        <h1 style="margin:8px 0 0 0;">AI Release Readiness and Program Risk Intelligence</h1>
        <p class="muted" style="margin-top:10px;">
            A concise decision-support view for senior stakeholders to assess readiness, identify top blockers, and assign action quickly.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

latest_file, df = load_data()
if latest_file is None or df.empty:
    st.warning("No results file found yet. Run app.py to generate program risk decisions.")
    st.stop()

st.markdown(
    f"""
    <div class="panel-card">
        <strong>Loaded decision log:</strong> {latest_file}
    </div>
    """,
    unsafe_allow_html=True,
)

top_risk = df.sort_values(by="risk_score", ascending=False).iloc[0]
blocking_count = int((df["blocking_flag"] == "Yes").sum()) if "blocking_flag" in df.columns else 0
high_risk_count = int((df["risk_level"] == "HIGH").sum()) if "risk_level" in df.columns else 0
no_go_count = int((df["release_readiness_status"] == "NO_GO").sum()) if "release_readiness_status" in df.columns else 0
top_blocker = df.sort_values(by=["blocking_flag", "risk_score", "confidence_score"], ascending=[False, False, False]).iloc[0]
top_blocker_owner = top_blocker["action_owner"] if "action_owner" in df.columns and not df.empty else "Program Manager"
top_blocker_title = display_issue_title(top_blocker)

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
with summary_col1:
    render_summary_card("NO-GO items", no_go_count, "Issues currently flagged as not ready to release", "#fca5a5")
with summary_col2:
    render_summary_card("Direct release blockers", blocking_count, "Issues directly impacting release readiness", "#fde68a")
with summary_col3:
    render_summary_card("High-risk concerns", high_risk_count, "Issues needing close leadership attention", "#fca5a5")
with summary_col4:
    render_summary_card("Owner for top blocker", top_blocker_owner, f"Mapped from the highest-severity issue: {top_blocker_title}", "#93c5fd")

st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown("## Focus filters")
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    risk_filter = st.selectbox("Risk level", ["All", "LOW", "MEDIUM", "HIGH"])
with filter_col2:
    risk_types = ["All"] + sorted(df["risk_type"].dropna().astype(str).unique().tolist()) if "risk_type" in df.columns else ["All"]
    type_filter = st.selectbox("Risk type", risk_types)
with filter_col3:
    readiness_values = ["All"] + sorted(df["release_readiness_status"].dropna().astype(str).unique().tolist()) if "release_readiness_status" in df.columns else ["All"]
    readiness_filter = st.selectbox("Readiness status", readiness_values)

filtered = df.copy()
if risk_filter != "All":
    filtered = filtered[filtered["risk_level"] == risk_filter]
if type_filter != "All":
    filtered = filtered[filtered["risk_type"] == type_filter]
if readiness_filter != "All":
    filtered = filtered[filtered["release_readiness_status"] == readiness_filter]

filtered_high_risk_count = int((filtered["risk_level"] == "HIGH").sum()) if "risk_level" in filtered.columns else 0
filtered_medium_risk_count = int((filtered["risk_level"] == "MEDIUM").sum()) if "risk_level" in filtered.columns else 0
filtered_low_risk_count = int((filtered["risk_level"] == "LOW").sum()) if "risk_level" in filtered.columns else 0
filtered_no_go_count = int((filtered["release_readiness_status"] == "NO_GO").sum()) if "release_readiness_status" in filtered.columns else 0
filtered_blocking_count = int((filtered["blocking_flag"] == "Yes").sum()) if "blocking_flag" in filtered.columns else 0

st.markdown(
    f"""
    <div class="muted" style="margin-top:8px;">
        Total issues in this view: <strong>{len(filtered)}</strong>.
        Severity split: <strong>{filtered_high_risk_count} High</strong>,
        <strong>{filtered_medium_risk_count} Medium</strong>,
        <strong>{filtered_low_risk_count} Low</strong>.
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

action_section_title = "## Top blockers requiring action" if filtered_blocking_count > 0 else "## Priority issues requiring action"
st.markdown(action_section_title)
if filtered.empty:
    st.info("No records matched the selected filters.")
else:
    top_actions = filtered.sort_values(by=["blocking_flag", "risk_score", "confidence_score"], ascending=[False, False, False]).head(3)
    action_cols = st.columns(min(3, len(top_actions)))
    for idx, (_, row) in enumerate(top_actions.iterrows()):
        with action_cols[idx]:
            render_action_card(row)

overview_col1, overview_col2 = st.columns(2)
with overview_col1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### Readiness distribution")
    if not filtered.empty and "release_readiness_status" in filtered.columns:
        readiness_counts = filtered["release_readiness_status"].value_counts().rename_axis("release_readiness_status").reset_index(name="count")
        st.plotly_chart(
            build_bar_chart(readiness_counts, "release_readiness_status", "count", "release_readiness_status", READINESS_COLORS),
            width="stretch",
        )
    else:
        st.info("No readiness data available.")
    st.markdown("</div>", unsafe_allow_html=True)

with overview_col2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### Risk mix")
    if not filtered.empty and "risk_type" in filtered.columns:
        type_counts = filtered["risk_type"].value_counts().rename_axis("risk_type").reset_index(name="count")
        risk_type_color_map = {risk_type: RISK_TYPE_COLORS.get(risk_type, "#93c5fd") for risk_type in type_counts["risk_type"].tolist()}
        st.plotly_chart(
            build_bar_chart(type_counts, "risk_type", "count", "risk_type", risk_type_color_map),
            width="stretch",
        )
    else:
        st.info("No risk type data available.")
    st.markdown("</div>", unsafe_allow_html=True)

owner_col1, owner_col2 = st.columns(2)
with owner_col1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### Recommended owners")
    if not filtered.empty and "action_owner" in filtered.columns:
        owner_counts = filtered["action_owner"].value_counts().rename_axis("action_owner").reset_index(name="count")
        owner_color_map = build_dynamic_color_map(owner_counts["action_owner"].tolist(), OWNER_PALETTE)
        st.plotly_chart(
            build_bar_chart(owner_counts, "action_owner", "count", "action_owner", owner_color_map),
            width="stretch",
        )
    else:
        st.info("No owner data available.")
    st.markdown("</div>", unsafe_allow_html=True)

with owner_col2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### High-risk score by issue")
    if not filtered.empty:
        score_view = filtered[["issue_title", "risk_score", "risk_level"]].copy() if "issue_title" in filtered.columns else filtered[["project_name", "risk_score", "risk_level"]].copy()
        label_col = "issue_title" if "issue_title" in score_view.columns else "project_name"
        st.plotly_chart(build_bar_chart(score_view, label_col, "risk_score", "risk_level", RISK_COLORS), width="stretch")
    else:
        st.info("No score data available.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("## Detailed issue review")
with st.expander("Open detailed analysis"):
    if filtered.empty:
        st.info("No detailed records matched the selected filters.")
    else:
        for _, row in filtered.sort_values(by=["risk_score", "confidence_score"], ascending=False).iterrows():
            render_detail_card(row)

st.markdown("## Executive evidence table")
table_columns = [
    "timestamp",
    "project_name",
    "milestone",
    "release_readiness_status",
    "blocking_flag",
    "risk_level",
    "risk_type",
    "action_owner",
    "recommended_action",
]
table_view = filtered[[col for col in table_columns if col in filtered.columns]].copy()
st.dataframe(table_view, width="stretch", hide_index=True)
st.download_button(
    "Download filtered decisions as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_program_risk_decisions.csv",
    mime="text/csv",
)
