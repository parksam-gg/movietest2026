import pandas as pd
import plotly.express as px
import streamlit as st

# ──────────────────────────────────────────────
# 기본 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="영화 데이터 그래프 도감 2", page_icon="🎬", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# ──────────────────────────────────────────────
# 데이터 불러오기
# ──────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 개봉일: 여덟 자리 숫자 → 날짜형
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")

    # 장르: '드라마|멜로/로맨스'처럼 여러 개면 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    return df


df = load_data()

st.caption(
    f"1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한 **{len(df)}편**의 요약표입니다. "
    "장르가 여러 개인 영화는 첫 번째 장르만 사용했습니다."
)

with st.expander("데이터 미리 보기"):
    st.dataframe(df, use_container_width=True)


# ──────────────────────────────────────────────
# 그래프 구역을 만드는 도우미
#   - 제목 → 그래프 → '이 그래프로 알 수 있는 것' 자리 → 구분선
# ──────────────────────────────────────────────
def graph_section(title: str, fig, insight: str = "", key: str = ""):
    st.divider()
    st.subheader(title)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.info(insight if insight else "여기에 한 문장으로 적어 보세요.")


# ──────────────────────────────────────────────
# 그래프 1. 장르별 영화 편수 (도넛 그래프)
# ──────────────────────────────────────────────
genre_count = (
    df["genre"]
    .value_counts()
    .rename_axis("genre")
    .reset_index(name="count")
)

fig1 = px.pie(
    genre_count,
    names="genre",
    values="count",
    hole=0.45,
    title="장르별 영화 편수",
)
fig1.update_traces(
    textinfo="label+percent",
    textposition="inside",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig1.update_layout(
    legend_title_text="장르",
    margin=dict(t=60, b=20, l=20, r=20),
)

graph_section(
    "1. 장르별 영화 편수",
    fig1,
    insight="",  # 이 그래프로 알 수 있는 것 한 문장을 여기에 적어 주세요.
    key="fig_genre_donut",
)
