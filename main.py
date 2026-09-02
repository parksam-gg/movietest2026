import numpy as np
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
    st.dataframe(df, width="stretch")


# ──────────────────────────────────────────────
# 그래프 구역을 만드는 도우미
#   - 제목 → 그래프 → '이 그래프로 알 수 있는 것' 자리 → 구분선
# ──────────────────────────────────────────────
def graph_section(title: str, fig, insight: str = "", key: str = ""):
    st.divider()
    st.subheader(title)
    st.plotly_chart(fig, width="stretch", key=key)
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


# ──────────────────────────────────────────────
# 그래프 2. 장르 안의 영화 (트리맵, 칸 크기 = 총 관객)
# ──────────────────────────────────────────────
fig2 = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    color="genre",
    title="장르별 영화 트리맵 (칸 크기 = 총 관객)",
)
fig2.update_traces(
    textinfo="label",
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>",
)
fig2.update_layout(
    height=650,
    margin=dict(t=60, b=20, l=20, r=20),
)

graph_section(
    "2. 장르 안의 영화 - 총 관객 트리맵",
    fig2,
    insight="",  # 이 그래프로 알 수 있는 것 한 문장을 여기에 적어 주세요.
    key="fig_genre_treemap",
)


# ──────────────────────────────────────────────
# 그래프 3. 총 관객 히스토그램
# ──────────────────────────────────────────────
n_bins = 30
counts, edges = np.histogram(df["total_audi"], bins=n_bins)
bin_size = edges[1] - edges[0]

fig3 = px.histogram(
    df,
    x="total_audi",
    title="총 관객 분포 (히스토그램)",
    labels={"total_audi": "총 관객(명)"},
)
fig3.update_traces(
    xbins=dict(start=edges[0], end=edges[-1], size=bin_size),
    hovertemplate="총 관객 구간: %{x}<br>영화 편수: %{y}편<extra></extra>",
)
fig3.update_layout(yaxis_title="영화 편수", bargap=0.05, margin=dict(t=60, b=20, l=20, r=20))

# 그래프 아래 문구용 계산
top_bin = int(np.argmax(counts))
bin_lo, bin_hi = edges[top_bin], edges[top_bin + 1]
share = counts[top_bin] / len(df) * 100
best = df.loc[df["total_audi"].idxmax()]

graph_section(
    "3. 총 관객 히스토그램",
    fig3,
    insight="",  # 이 그래프로 알 수 있는 것 한 문장을 여기에 적어 주세요.
    key="fig_total_audi_hist",
)
st.markdown(
    f"- 가장 많은 영화가 몰린 구간: **{bin_lo:,.0f}명 ~ {bin_hi:,.0f}명** "
    f"({counts[top_bin]}편, 전체의 {share:.1f}%)\n"
    f"- 관객이 가장 많은 영화: **{best['movieNm']}** ({best['total_audi']:,}명, {best['genre']})"
)


# ──────────────────────────────────────────────
# 그래프 4. 개봉일 스크린수 × 총 관객 산점도
# ──────────────────────────────────────────────
fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={"first_scrn": ":,", "total_audi": ":,", "genre": True},
    title="개봉일 스크린수와 총 관객",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객(명)", "genre": "장르"},
)
fig4.update_traces(marker=dict(size=9, opacity=0.8))
fig4.update_layout(margin=dict(t=60, b=20, l=20, r=20))

graph_section(
    "4. 개봉일 스크린수 × 총 관객 산점도",
    fig4,
    insight="",  # 이 그래프로 알 수 있는 것 한 문장을 여기에 적어 주세요.
    key="fig_scrn_audi_scatter",
)


# ──────────────────────────────────────────────
# 그래프 5. 장르별 총 관객 상자 그림 (영화 10편 이상 장르만)
# ──────────────────────────────────────────────
genre_size = df["genre"].value_counts()
big_genres = genre_size[genre_size >= 10].index.tolist()
df_box = df[df["genre"].isin(big_genres)]

fig5 = px.box(
    df_box,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
    hover_data={"total_audi": ":,", "genre": False},
    category_orders={"genre": big_genres},
    title=f"장르별 총 관객 상자 그림 (영화 10편 이상인 {len(big_genres)}개 장르)",
    labels={"genre": "장르", "total_audi": "총 관객(명)"},
)
fig5.update_layout(showlegend=False, margin=dict(t=60, b=20, l=20, r=20))

graph_section(
    "5. 장르별 총 관객 상자 그림",
    fig5,
    insight="",  # 이 그래프로 알 수 있는 것 한 문장을 여기에 적어 주세요.
    key="fig_genre_box",
)


# ──────────────────────────────────────────────
# 그래프 6. 버블 그래프 (점 크기 = 첫 주 관객)
# ──────────────────────────────────────────────
fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    size="first_week_audi",
    size_max=45,
    hover_name="movieNm",
    hover_data={"first_scrn": ":,", "total_audi": ":,", "first_week_audi": ":,", "genre": True},
    title="개봉일 스크린수와 총 관객 (점 크기 = 첫 주 관객)",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객(명)",
        "first_week_audi": "첫 주 관객(명)",
        "genre": "장르",
    },
)
fig6.update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color="white")))
fig6.update_layout(margin=dict(t=60, b=20, l=20, r=20))

graph_section(
    "6. 스크린수 × 총 관객 버블 그래프 (크기 = 첫 주 관객)",
    fig6,
    insight="",  # 이 그래프로 알 수 있는 것 한 문장을 여기에 적어 주세요.
    key="fig_scrn_audi_bubble",
)


# ──────────────────────────────────────────────
# 그래프 7. 제작 국가 → 장르 선버스트 (칸 크기 = 영화 편수)
# ──────────────────────────────────────────────
df_sun = df.assign(영화편수=1)

fig7 = px.sunburst(
    df_sun,
    path=["nation", "genre"],
    values="영화편수",
    title="제작 국가 → 장르 선버스트 (칸 크기 = 영화 편수)",
)
fig7.update_traces(
    textinfo="label+value",
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percentRoot:.1%}<extra></extra>",
)
fig7.update_layout(height=650, margin=dict(t=60, b=20, l=20, r=20))

graph_section(
    "7. 제작 국가 → 장르 선버스트",
    fig7,
    insight="",  # 이 그래프로 알 수 있는 것 한 문장을 여기에 적어 주세요.
    key="fig_nation_genre_sunburst",
)
