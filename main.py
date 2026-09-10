import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")


# [1. 데이터 불러오기 & 캐싱]
# @st.cache_data를 사용해 데이터를 매번 다시 받지 않고 저장해서 재사용합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(빈 값)가 포함된 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 문자열에서 datetime(날짜) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 기준일자 오름차순으로 정렬
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드 실행
df = load_data()

# 대시보드 제목
st.title("🎬 영화 박스오피스 데이터 대시보드")

# [3. 영화 선택 기능]
# 영화별 최고 누적관객수를 구해 내림차순으로 목록 정렬
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사용자 영화 선택 드롭다운 목록
selected_movie = st.selectbox("🎥 분석할 영화를 선택하세요", movie_order)

# 선택한 영화의 데이터만 추출
filtered_df = df[df["영화명"] == selected_movie]


# [4. 첫 번째 그래프 - 일별 관객수 선 그래프]
st.write("---")
st.subheader("📈 1. 선택한 영화의 일별 관객수 추이")

fig_line = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"[{selected_movie}] 일별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "관객수 (명)"},
    markers=True,
)

st.plotly_chart(fig_line, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 초반 관객수 집중도와 주말/평일 간의 관객수 변동 패턴을 파악할 수 있습니다."
)


# [5. 두 번째 그래프 - 누적 관객수 영역 차트]
st.write("---")
st.subheader("🌊 2. 선택한 영화의 누적 관객수 추이")

fig_area = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"[{selected_movie}] 누적 관객수 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)"},
)

st.plotly_chart(fig_area, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 총 관객수가 누적되는 상승 곡선과 주요 흥행 구간(급격히 증가하는 시기)을 직관적으로 확인할 수 있습니다."
)


# [6. 세 번째 그래프 - 장기 흥행 TOP 5 영화 누적 관객수 비교]
st.write("---")
st.subheader("🏆 3. 장기 흥행(20일 이상 상위권) TOP 5 영화 누적 관객수 비교")

top10_df = df[df["순위"] <= 10] if "순위" in df.columns else df
movie_appearance_days = top10_df.groupby("영화명")["기준일자"].nunique()
movies_over_20days = movie_appearance_days[movie_appearance_days >= 20].index

top5_longterm_movies = (
    df[df["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

top5_longterm_df = df[df["영화명"].isin(top5_longterm_movies)]

fig_top5 = px.line(
    top5_longterm_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP 10 20일 이상 유지 영화 중 누적 관객수 TOP 5 비교",
    labels={
        "기준일자": "날짜",
        "누적관객수": "누적 관객수 (명)",
        "영화명": "영화 제목",
    },
)

st.plotly_chart(fig_top5, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 단기 반짝 흥행을 제외하고, 박스오피스 상위권(TOP 10)에 20일 이상 꾸준히 머무른 롱런 영화들 중 최고 흥행작 5개 편의 누적관객 성장 속도 및 차이를 파악할 수 있습니다."
)


# [7. 네 번째 그래프 - 전체 박스오피스 관객수 7일 이동평균선]
st.write("---")
st.subheader("📉 4. 전체 박스오피스 일별 관객수 및 7일 이동평균 추이")

# 1) 기준일자별 TOP 10 영화의 해당일관객수 전체 합계 구하기
top10_daily = df[df["순위"] <= 10] if "순위" in df.columns else df
daily_total = top10_daily.groupby("기준일자")["해당일관객수"].sum().reset_index()

# 2) 7일 이동평균(Rolling Mean) 계산
daily_total["7일_이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()
)

# 3) Plotly graph_objects로 원본 선과 이동평균 선을 겹쳐서 작성
fig_ma = go.Figure()

# 원본 일별 관객수 선 (연하고 얇은 선)
fig_ma.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 관객수 (합계)",
        line=dict(color="rgba(180, 180, 180, 0.5)", width=1.5),
    )
)

# 7일 이동평균 선 (진하고 두꺼운 선)
fig_ma.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#1f77b4", width=3),
    )
)

# 그래프 레이아웃 설정
fig_ma.update_layout(
    title="전체 박스오피스 일별 관객수 합계 및 7일 이동평균선",
    xaxis_title="날짜",
    yaxis_title="총 관객수 (명)",
    hovermode="x unified",
)

st.plotly_chart(fig_ma, use_container_width=True)

# 네 번째 그래프 설명 문구
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 주말과 평일 사이의 일별 관객수 급변에 따른 착시를 줄이고, 전체 영화 시장의 전반적인 흥행 흐름과 성수기·비수기 트렌드를 부드러운 곡선으로 파악할 수 있습니다."
)


# [8. 구역 나누기 - 향후 그래프 추가용 구역]
st.write("---")
st.subheader("📊 5. 추가 분석 (예정)")
st.write("📌 *이 구역에는 추후 새로운 분석 그래프가 추가될 예정입니다.*")
