import streamlit as st
import json
import os
from datetime import date, datetime, timedelta
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uniform Check-In",
    page_icon="📋",
    layout="wide",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_FILE    = "data/records.json"
CONFIG_FILE  = "data/config.json"
os.makedirs("data", exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

def iso(d: date) -> str:
    return d.isoformat()

def weekdays_in_range(start: date, end: date):
    days = []
    cur = start
    while cur <= end:
        if cur.weekday() < 5:   # Mon–Fri
            days.append(cur)
        cur += timedelta(days=1)
    return days

# ── Default config ────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "students": [],
    "uniform_items": [
        "Shirt / Blouse",
        "Pants / Skirt",
        "Shoes",
        "Tie / Ribbon",
        "Name Badge",
        "Socks",
        "Belt",
    ],
}

# ── Load state ────────────────────────────────────────────────────────────────
config  = load_json(CONFIG_FILE, DEFAULT_CONFIG)
records = load_json(DATA_FILE,   {})

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/checklist.png", width=60)
st.sidebar.title("📋 Uniform Check-In")
page = st.sidebar.radio(
    "Navigate",
    ["📅 Daily Check-In", "📊 Weekly Summary", "📆 Monthly Summary", "⚙️ Settings"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Today: **{date.today().strftime('%A, %d %b %Y')}**")

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 – DAILY CHECK-IN
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📅 Daily Check-In":
    st.title("📅 Daily Uniform Check-In")

    if not config["students"]:
        st.warning("No students yet! Go to **⚙️ Settings** to add your class list.")
        st.stop()

    col_date, col_space = st.columns([1, 3])
    with col_date:
        selected_date = st.date_input("Select date", value=date.today())
    if selected_date.weekday() >= 5:
        st.info("ℹ️ This is a weekend. Check-ins are for Mon–Fri only.")
        st.stop()

    date_key = iso(selected_date)
    day_data  = records.get(date_key, {})

    st.markdown("---")
    st.subheader(f"Class on {selected_date.strftime('%A, %d %B %Y')}")

    uniform_items = config["uniform_items"]

    # Header row
    cols = st.columns([2, 1, 1] + [1]*len(uniform_items) + [2])
    headers = ["Student", "Checked", "Status"] + uniform_items + ["Notes"]
    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")
    st.markdown("---")

    updated_day = {}

    for student in config["students"]:
        prev = day_data.get(student, {})
        cols = st.columns([2, 1, 1] + [1]*len(uniform_items) + [2])

        # Name
        cols[0].markdown(f"**{student}**")

        # Checked in
        checked = cols[1].checkbox(
            "✔", value=prev.get("checked", False),
            key=f"{date_key}_{student}_checked",
            label_visibility="collapsed",
        )

        # Status
        status_options = ["Present", "Late", "Absent", "Sick"]
        default_status = prev.get("status", "Present")
        status = cols[2].selectbox(
            "Status", status_options,
            index=status_options.index(default_status),
            key=f"{date_key}_{student}_status",
            label_visibility="collapsed",
        )

        # Uniform items (only meaningful if checked in)
        item_vals = {}
        for i, item in enumerate(uniform_items):
            if checked and status == "Present":
                val = cols[3+i].checkbox(
                    item,
                    value=prev.get("items", {}).get(item, True),
                    key=f"{date_key}_{student}_{item}",
                    label_visibility="collapsed",
                )
            else:
                cols[3+i].markdown("—")
                val = False
            item_vals[item] = val

        # Notes
        notes = cols[3+len(uniform_items)].text_input(
            "Notes",
            value=prev.get("notes", ""),
            key=f"{date_key}_{student}_notes",
            label_visibility="collapsed",
            placeholder="e.g. missing badge",
        )

        updated_day[student] = {
            "checked": checked,
            "status":  status,
            "items":   item_vals,
            "notes":   notes,
        }

    st.markdown("---")
    if st.button("💾 Save Today's Check-In", type="primary", use_container_width=True):
        records[date_key] = updated_day
        save_json(DATA_FILE, records)
        st.success(f"✅ Saved check-in for {selected_date.strftime('%A, %d %B %Y')}!")
        st.balloons()

    # Quick stats
    st.markdown("---")
    st.subheader("Quick Stats for Today")
    total    = len(config["students"])
    checked_in = sum(1 for v in updated_day.values() if v["checked"])
    absent   = sum(1 for v in updated_day.values() if v["status"] == "Absent")
    late     = sum(1 for v in updated_day.values() if v["status"] == "Late")
    sick     = sum(1 for v in updated_day.values() if v["status"] == "Sick")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Students", total)
    c2.metric("Checked In",     checked_in)
    c3.metric("Absent",         absent)
    c4.metric("Late",           late)
    c5.metric("Sick",           sick)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 – WEEKLY SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Weekly Summary":
    st.title("📊 Weekly Summary")

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    col1, col2 = st.columns(2)
    week_start = col1.date_input("Week starting (Monday)", value=start_of_week)
    week_end   = week_start + timedelta(days=4)
    col2.markdown(f"**Week:** {week_start.strftime('%d %b')} → {week_end.strftime('%d %b %Y')}")

    days = weekdays_in_range(week_start, week_end)
    students = config["students"]

    if not students:
        st.warning("No students configured. Go to ⚙️ Settings.")
        st.stop()

    # Build summary table
    rows = []
    for student in students:
        row = {"Student": student}
        missing_any = []
        for d in days:
            dk  = iso(d)
            day = records.get(dk, {}).get(student, {})
            status = day.get("status", "—")
            if not day:
                status = "—"
            row[d.strftime("%a %d")] = status
            if day.get("checked"):
                missing = [item for item, ok in day.get("items", {}).items() if not ok]
                if missing:
                    missing_any += missing
        row["Missing Items (week)"] = ", ".join(set(missing_any)) if missing_any else "✅ None"
        rows.append(row)

    df = pd.DataFrame(rows).set_index("Student")

    def colour_status(val):
        colours = {
            "Present": "background-color:#d4edda",
            "Late":    "background-color:#fff3cd",
            "Absent":  "background-color:#f8d7da",
            "Sick":    "background-color:#d1ecf1",
            "—":       "color:#aaa",
        }
        return colours.get(val, "")

    day_cols = [d.strftime("%a %d") for d in days]
    st.dataframe(
        df.style.applymap(colour_status, subset=day_cols),
        use_container_width=True,
        height=600,
    )

    # Attendance counts
    st.markdown("---")
    st.subheader("Attendance Counts")
    count_rows = []
    for student in students:
        counts = {"Student": student, "Present": 0, "Late": 0, "Absent": 0, "Sick": 0, "Not Recorded": 0}
        for d in days:
            day = records.get(iso(d), {}).get(student, {})
            s = day.get("status", "Not Recorded") if day else "Not Recorded"
            if s in counts:
                counts[s] += 1
            else:
                counts["Not Recorded"] += 1
        count_rows.append(counts)

    st.dataframe(pd.DataFrame(count_rows).set_index("Student"), use_container_width=True)

    # Download
    csv = df.reset_index().to_csv(index=False).encode()
    st.download_button("⬇️ Download Weekly CSV", csv,
                       f"weekly_{week_start}.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 – MONTHLY SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📆 Monthly Summary":
    st.title("📆 Monthly Summary")

    import calendar
    today = date.today()
    month = st.selectbox("Month", list(range(1, 13)),
                         index=today.month - 1,
                         format_func=lambda m: calendar.month_name[m])
    year  = st.number_input("Year", min_value=2020, max_value=2099, value=today.year)

    first_day = date(year, month, 1)
    last_day  = date(year, month, calendar.monthrange(year, month)[1])
    days = weekdays_in_range(first_day, last_day)

    students = config["students"]
    if not students:
        st.warning("No students configured.")
        st.stop()

    st.markdown(f"**{calendar.month_name[month]} {year}** — {len(days)} school days")

    rows = []
    for student in students:
        counts = {"Student": student, "School Days": len(days),
                  "Present": 0, "Late": 0, "Absent": 0, "Sick": 0,
                  "Not Recorded": 0, "Uniform Issues": 0}
        for d in days:
            day = records.get(iso(d), {}).get(student, {})
            s = day.get("status", "Not Recorded") if day else "Not Recorded"
            if s in counts:
                counts[s] += 1
            else:
                counts["Not Recorded"] += 1
            if day.get("checked"):
                issues = sum(1 for ok in day.get("items", {}).values() if not ok)
                counts["Uniform Issues"] += issues
        rows.append(counts)

    df = pd.DataFrame(rows).set_index("Student")
    st.dataframe(df, use_container_width=True, height=600)

    # Top offenders
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔴 Most Absences")
        st.dataframe(df[["Absent"]].sort_values("Absent", ascending=False).head(5))
    with col2:
        st.subheader("⚠️ Most Uniform Issues")
        st.dataframe(df[["Uniform Issues"]].sort_values("Uniform Issues", ascending=False).head(5))

    csv = df.reset_index().to_csv().encode()
    st.download_button("⬇️ Download Monthly CSV", csv,
                       f"monthly_{year}_{month:02}.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 – SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")

    # ── Student list ──────────────────────────────────────────────────────────
    st.subheader("👥 Student List")
    st.caption("One name per line. Changes are saved when you click Save.")

    students_text = st.text_area(
        "Students (one per line)",
        value="\n".join(config["students"]),
        height=300,
        label_visibility="collapsed",
        placeholder="e.g.\nAlice Smith\nBob Jones\n...",
    )

    st.markdown("---")

    # ── Uniform items ─────────────────────────────────────────────────────────
    st.subheader("👔 Uniform Items to Check")
    st.caption("One item per line.")

    items_text = st.text_area(
        "Uniform Items",
        value="\n".join(config["uniform_items"]),
        height=220,
        label_visibility="collapsed",
        placeholder="e.g.\nShirt / Blouse\nPants / Skirt\n...",
    )

    st.markdown("---")
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        new_students = [s.strip() for s in students_text.splitlines() if s.strip()]
        new_items    = [i.strip() for i in items_text.splitlines() if i.strip()]
        config["students"]      = new_students
        config["uniform_items"] = new_items
        save_json(CONFIG_FILE, config)
        st.success(f"✅ Saved! {len(new_students)} students, {len(new_items)} uniform items.")
        st.rerun()

    # ── Danger zone ───────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🗑️ Danger Zone"):
        st.warning("This will permanently delete ALL check-in records.")
        if st.button("Delete All Records", type="secondary"):
            save_json(DATA_FILE, {})
            st.error("All records deleted.")
