import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="My Student Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# File Configuration
# ============================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATA_FILE = DATA_DIR / "expenses.csv"

# ============================================================
# Categories
# ============================================================

CATEGORIES = [
    "食材",
    "外食",
    "交通",
    "日用品",
    "娱乐",
    "购物",
    "住宿",
    "学习",
    "其他"
]

CURRENCIES = ["SGD", "RMB"]


# ============================================================
# Load Data
# ============================================================

def load_data():

    if not DATA_FILE.exists():

        df = pd.DataFrame(
            columns=[
                "id",
                "date",
                "category",
                "item",
                "currency",
                "amount"
            ]
        )

        df.to_csv(DATA_FILE, index=False)

        return df

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "id",
                "date",
                "category",
                "item",
                "currency",
                "amount"
            ]
        )

    df["date"] = pd.to_datetime(df["date"])

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    return df


# ============================================================
# Save Data
# ============================================================

def save_data(df):

    df.to_csv(
        DATA_FILE,
        index=False
    )


# ============================================================
# Initialize Data
# ============================================================

if "expenses" not in st.session_state:

    st.session_state.expenses = load_data()


# ============================================================
# Helper Functions
# ============================================================

def add_expense(
    expense_date,
    category,
    item,
    currency,
    amount
):

    df = st.session_state.expenses.copy()

    if len(df) == 0:
        new_id = 1
    else:
        new_id = int(df["id"].max()) + 1

    new_row = pd.DataFrame(
        [{
            "id": new_id,
            "date": pd.to_datetime(expense_date),
            "category": category,
            "item": item,
            "currency": currency,
            "amount": amount
        }]
    )

    df = pd.concat(
        [df, new_row],
        ignore_index=True
    )

    st.session_state.expenses = df

    save_data(df)


def delete_expense(expense_id):

    df = st.session_state.expenses.copy()

    df = df[
        df["id"] != expense_id
    ]

    st.session_state.expenses = df

    save_data(df)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.title("💰 Finance Tracker")

    st.caption(
        "Singapore Student Personal Finance Dashboard"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📖 浏览",
            "➕ 增加",
            "✏️ 删改",
            "📊 统计"
        ]
    )

    st.divider()

    st.info(
        "记录你的日常消费，并通过数据可视化了解自己的消费习惯。"
    )


# ============================================================
# Main Header
# ============================================================

st.title("🇸🇬 My Student Finance Tracker")

st.caption(
    "Personal Expense Management & Analytics"
)


# ============================================================
# PAGE 1 — Browse
# ============================================================

if page == "📖 浏览":

    st.header("📖 浏览消费记录")

    df = st.session_state.expenses.copy()

    if df.empty:

        st.info(
            "目前还没有消费记录。可以前往「增加」页面添加第一笔消费。"
        )

    else:

        # ----------------------------------------------------
        # Filters
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            categories = st.multiselect(
                "分类",
                CATEGORIES,
                default=[]
            )

        with col2:

            currencies = st.multiselect(
                "币种",
                CURRENCIES,
                default=[]
            )

        with col3:

            months = sorted(
                df["date"]
                .dt.strftime("%Y-%m")
                .unique(),
                reverse=True
            )

            selected_months = st.multiselect(
                "月份",
                months,
                default=[]
            )

        filtered = df.copy()

        if categories:

            filtered = filtered[
                filtered["category"].isin(categories)
            ]

        if currencies:

            filtered = filtered[
                filtered["currency"].isin(currencies)
            ]

        if selected_months:

            filtered = filtered[
                filtered["date"]
                .dt.strftime("%Y-%m")
                .isin(selected_months)
            ]

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        st.subheader("消费概览")

        c1, c2, c3 = st.columns(3)

        sgd_total = filtered.loc[
            filtered["currency"] == "SGD",
            "amount"
        ].sum()

        rmb_total = filtered.loc[
            filtered["currency"] == "RMB",
            "amount"
        ].sum()

        transaction_count = len(filtered)

        c1.metric(
            "SGD 消费",
            f"S$ {sgd_total:,.2f}"
        )

        c2.metric(
            "RMB 消费",
            f"¥ {rmb_total:,.2f}"
        )

        c3.metric(
            "记录数量",
            transaction_count
        )

        st.divider()

        # ----------------------------------------------------
        # Display Table
        # ----------------------------------------------------

        display_df = filtered.copy()

        display_df["date"] = display_df[
            "date"
        ].dt.strftime("%Y-%m-%d")

        display_df = display_df[
            [
                "date",
                "category",
                "item",
                "currency",
                "amount"
            ]
        ]

        display_df.columns = [
            "日期",
            "分类",
            "消费内容",
            "币种",
            "金额"
        ]

        display_df = display_df.sort_values(
            "日期",
            ascending=False
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# PAGE 2 — Add
# ============================================================

elif page == "➕ 增加":

    st.header("➕ 增加消费记录")

    st.write(
        "记录一笔新的消费。"
    )

    with st.form("add_expense_form"):

        expense_date = st.date_input(
            "日期",
            value=date.today()
        )

        category = st.selectbox(
            "分类",
            CATEGORIES
        )

        item = st.text_input(
            "具体消费",
            placeholder="例如：学校食阁午餐"
        )

        currency = st.selectbox(
            "币种",
            CURRENCIES
        )

        amount = st.number_input(
            "价格",
            min_value=0.00,
            step=0.10,
            format="%.2f"
        )

        submitted = st.form_submit_button(
            "💾 保存消费记录",
            use_container_width=True
        )

        if submitted:

            if not item.strip():

                st.error(
                    "请输入具体消费内容。"
                )

            elif amount <= 0:

                st.error(
                    "金额必须大于 0。"
                )

            else:

                add_expense(
                    expense_date,
                    category,
                    item.strip(),
                    currency,
                    amount
                )

                st.success(
                    "消费记录已成功添加！"
                )

                st.rerun()


# ============================================================
# PAGE 3 — Edit / Delete
# ============================================================

elif page == "✏️ 删改":

    st.header("✏️ 修改 / 删除消费记录")

    df = st.session_state.expenses.copy()

    if df.empty:

        st.info(
            "目前没有可以修改或删除的记录。"
        )

    else:

        df = df.sort_values(
            "date",
            ascending=False
        )

        # ----------------------------------------------------
        # Select record
        # ----------------------------------------------------

        record_options = {}

        for _, row in df.iterrows():

            label = (
                f"{row['date'].strftime('%Y-%m-%d')} | "
                f"{row['item']} | "
                f"{row['currency']} "
                f"{row['amount']:.2f}"
            )

            record_options[label] = int(row["id"])

        selected_label = st.selectbox(
            "选择需要修改或删除的记录",
            list(record_options.keys())
        )

        selected_id = record_options[
            selected_label
        ]

        selected_row = df[
            df["id"] == selected_id
        ].iloc[0]

        st.divider()

        # ----------------------------------------------------
        # Edit
        # ----------------------------------------------------

        st.subheader("编辑记录")

        with st.form("edit_form"):

            edit_date = st.date_input(
                "日期",
                value=selected_row["date"].date()
            )

            edit_category = st.selectbox(
                "分类",
                CATEGORIES,
                index=CATEGORIES.index(
                    selected_row["category"]
                )
            )

            edit_item = st.text_input(
                "具体消费",
                value=selected_row["item"]
            )

            edit_currency = st.selectbox(
                "币种",
                CURRENCIES,
                index=CURRENCIES.index(
                    selected_row["currency"]
                )
            )

            edit_amount = st.number_input(
                "价格",
                min_value=0.00,
                value=float(selected_row["amount"]),
                step=0.10,
                format="%.2f"
            )

            update_button = st.form_submit_button(
                "💾 保存修改",
                use_container_width=True
            )

            if update_button:

                df.loc[
                    df["id"] == selected_id,
                    "date"
                ] = pd.to_datetime(edit_date)

                df.loc[
                    df["id"] == selected_id,
                    "category"
                ] = edit_category

                df.loc[
                    df["id"] == selected_id,
                    "item"
                ] = edit_item

                df.loc[
                    df["id"] == selected_id,
                    "currency"
                ] = edit_currency

                df.loc[
                    df["id"] == selected_id,
                    "amount"
                ] = edit_amount

                st.session_state.expenses = df

                save_data(df)

                st.success(
                    "记录修改成功！"
                )

                st.rerun()

        # ----------------------------------------------------
        # Delete
        # ----------------------------------------------------

        st.divider()

        st.subheader("删除记录")

        st.warning(
            "删除操作不可恢复，请确认你选择的是正确的记录。"
        )

        if st.button(
            "🗑️ 删除这条记录",
            use_container_width=True
        ):

            delete_expense(
                selected_id
            )

            st.success(
                "记录已删除。"
            )

            st.rerun()


# ============================================================
# PAGE 4 — Statistics
# ============================================================

elif page == "📊 统计":

    st.header("📊 消费统计")

    df = st.session_state.expenses.copy()

    if df.empty:

        st.info(
            "目前没有足够的数据进行统计。"
        )

    else:

        df["month"] = df[
            "date"
        ].dt.to_period("M").astype(str)

        # ====================================================
        # Top-level Metrics
        # ====================================================

        st.subheader("💰 总体概览")

        c1, c2, c3, c4 = st.columns(4)

        sgd_total = df.loc[
            df["currency"] == "SGD",
            "amount"
        ].sum()

        rmb_total = df.loc[
            df["currency"] == "RMB",
            "amount"
        ].sum()

        average_transaction = df[
            "amount"
        ].mean()

        max_transaction = df[
            "amount"
        ].max()

        c1.metric(
            "SGD 总消费",
            f"S$ {sgd_total:,.2f}"
        )

        c2.metric(
            "RMB 总消费",
            f"¥ {rmb_total:,.2f}"
        )

        c3.metric(
            "平均单笔消费",
            f"{average_transaction:,.2f}"
        )

        c4.metric(
            "最大单笔消费",
            f"{max_transaction:,.2f}"
        )

        st.divider()

        # ====================================================
        # Monthly Statistics
        # ====================================================

        st.subheader("📅 月度消费")

        monthly = (
            df.groupby(
                ["month", "currency"]
            )["amount"]
            .sum()
            .reset_index()
        )

        fig_monthly = px.bar(
            monthly,
            x="month",
            y="amount",
            color="currency",
            barmode="group",
            title="Monthly Spending by Currency",
            labels={
                "month": "月份",
                "amount": "金额",
                "currency": "币种"
            }
        )

        st.plotly_chart(
            fig_monthly,
            use_container_width=True
        )

        # ====================================================
        # Category Pie Chart
        # ====================================================

        st.subheader("🥧 消费分类占比")

        col1, col2 = st.columns(2)

        with col1:

            selected_currency = st.selectbox(
                "选择币种",
                CURRENCIES,
                key="pie_currency"
            )

            category_data = df[
                df["currency"] == selected_currency
            ].groupby(
                "category"
            )["amount"].sum().reset_index()

            fig_pie = px.pie(
                category_data,
                names="category",
                values="amount",
                hole=0.35,
                title=f"{selected_currency} 消费分类占比"
            )

            st.plotly_chart(
                fig_pie,
                use_container_width=True
            )

        # ====================================================
        # Category Bar Chart
        # ====================================================

        with col2:

            fig_category = px.bar(
                category_data.sort_values(
                    "amount",
                    ascending=True
                ),
                x="amount",
                y="category",
                orientation="h",
                title=f"{selected_currency} 各分类消费",
                labels={
                    "amount": "金额",
                    "category": "分类"
                }
            )

            st.plotly_chart(
                fig_category,
                use_container_width=True
            )

        # ====================================================
        # Monthly Category Spending
        # ====================================================

        st.subheader("📊 每月分类消费")

        selected_currency_2 = st.selectbox(
            "统计币种",
            CURRENCIES,
            key="monthly_category_currency"
        )

        monthly_category = (
            df[
                df["currency"] == selected_currency_2
            ]
            .groupby(
                ["month", "category"]
            )["amount"]
            .sum()
            .reset_index()
        )

        fig_month_category = px.bar(
            monthly_category,
            x="month",
            y="amount",
            color="category",
            title=f"{selected_currency_2} 每月分类消费",
            labels={
                "month": "月份",
                "amount": "金额",
                "category": "分类"
            }
        )

        st.plotly_chart(
            fig_month_category,
            use_container_width=True
        )

        # ====================================================
        # Daily Spending Trend
        # ====================================================

        st.subheader("📈 每日消费趋势")

        selected_currency_3 = st.selectbox(
            "趋势币种",
            CURRENCIES,
            key="daily_currency"
        )

        daily = (
            df[
                df["currency"] == selected_currency_3
            ]
            .groupby("date")["amount"]
            .sum()
            .reset_index()
        )

        fig_daily = px.line(
            daily,
            x="date",
            y="amount",
            markers=True,
            title=f"{selected_currency_3} 每日消费趋势",
            labels={
                "date": "日期",
                "amount": "金额"
            }
        )

        st.plotly_chart(
            fig_daily,
            use_container_width=True
        )

        # ====================================================
        # Top Expenses
        # ====================================================

        st.subheader("🔥 单笔消费 TOP 10")

        top_expenses = df.sort_values(
            "amount",
            ascending=False
        ).head(10)

        top_display = top_expenses[
            [
                "date",
                "category",
                "item",
                "currency",
                "amount"
            ]
        ].copy()

        top_display["date"] = top_display[
            "date"
        ].dt.strftime("%Y-%m-%d")

        top_display.columns = [
            "日期",
            "分类",
            "消费",
            "币种",
            "金额"
        ]

        st.dataframe(
            top_display,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "Personal Finance Tracker · Built with Streamlit · "
    "For personal financial tracking and analytics"
)