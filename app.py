
"""12주차 직접 쓰기 앱: 배포할 수 있는 대시보드"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

COLORS = {"A": "#0072B2", "B": "#D55E00"}

st.set_page_config(page_title="지점 실적 탐색", layout="wide")
st.title("어느 지점의 실적이 더 좋은가")
st.caption(
    "출처: 수업용 가상 데이터(sales.csv) · "
    "2026년 1~12월 지점별 월 실적 · 금액 단위: 백만원"
)

# 1-3 데이터 경로
HERE = Path(__file__).parent


@st.cache_data
def load_data():
    file_path = HERE / "sales.csv"

    if not file_path.exists():
        st.error("sales.csv 파일이 없습니다.")
        st.stop()

    return pd.read_csv(file_path)


data = load_data()


# 2-2 사이드바 위젯 세 개
st.sidebar.header("조회 조건")

branches = st.sidebar.multiselect(
    "지점 선택",
    options=["A", "B"],
    default=["A", "B"]
)

month_range = st.sidebar.slider(
    "월 범위",
    min_value=1,
    max_value=12,
    value=(1, 12)
)

metric_name = st.sidebar.radio(
    "표시 지표",
    options=["매출", "영업이익"]
)

metric = {
    "매출": "sales",
    "영업이익": "profit"
}[metric_name]


# 빈 선택 처리
view = data[
    (data["branch"].isin(branches))
    & (data["month"].between(
        month_range[0], month_range[1]
    ))
].copy()

if view.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()


# 3-1 지표 카드 두 개
total = view[metric].sum()
count = len(view)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label=f"기간 {metric_name} 합계",
        value=f"{total:,.1f} 백만원"
    )

with col2:
    st.metric(
        label="표시 관측 수",
        value=f"{count}행"
    )


# 2-9 Plotly 차트 세 개
st.subheader("지점별 실적 분석")

chart1, chart2, chart3 = st.columns(3)

# 차트 1: 월별 추이
monthly = (
    view.groupby(["month", "branch"], as_index=False)[metric]
    .sum()
)

fig1 = px.line(
    monthly,
    x="month",
    y=metric,
    color="branch",
    markers=True,
    title=f"월별 {metric_name} 추이",
    color_discrete_map=COLORS
)

fig1.update_layout(
    xaxis_title="월",
    yaxis_title=f"{metric_name} (백만원)"
)

with chart1:
    st.plotly_chart(fig1, use_container_width=True)


# 차트 2: 지점별 기간 합계
branch_total = (
    view.groupby("branch", as_index=False)[metric]
    .sum()
)

fig2 = px.bar(
    branch_total,
    x="branch",
    y=metric,
    color="branch",
    title=f"지점별 기간 {metric_name} 합계",
    color_discrete_map=COLORS
)

fig2.update_layout(
    xaxis_title="지점",
    yaxis_title=f"{metric_name} (백만원)"
)

with chart2:
    st.plotly_chart(fig2, use_container_width=True)


# 차트 3: 지점별 영업이익률
profit_rate = (
    view.groupby("branch", as_index=False)[
        ["sales", "profit"]
    ]
    .sum()
)

profit_rate["profit_rate"] = (
    profit_rate["profit"]
    / profit_rate["sales"].where(
        profit_rate["sales"] != 0
    )
    * 100
)

fig3 = px.bar(
    profit_rate,
    x="branch",
    y="profit_rate",
    color="branch",
    title="지점별 기간 영업이익률",
    color_discrete_map=COLORS
)

fig3.update_layout(
    xaxis_title="지점",
    yaxis_title="영업이익률 (%)"
)

with chart3:
    st.plotly_chart(fig3, use_container_width=True)


# 4-1 표와 CSV 다운로드
st.subheader("선택한 데이터")

st.dataframe(
    view,
    use_container_width=True,
    hide_index=True
)

csv = view.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="선택 데이터 CSV 다운로드",
    data=csv,
    file_name="selected_sales.csv",
    mime="text/csv"
)
