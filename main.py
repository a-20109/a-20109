import pandas as pd
import plotly.express as px
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


# [5. 구역 나누기 - 첫 번째 섹션]
st.write("---")
st.subheader("📈 일별 관객수 추이")

# [4. 선그래프 그리기]
# Plotly를 이용한 일별 관객수 변화 선그래프 작성
fig = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"[{selected_movie}] 일별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "관객수 (명)"},
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 화면에 출력 (너비에 맞춤)
st.plotly_chart(fig, use_container_width=True)

# [5. 기타 - 알 수 있는 것 문구 자리]
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 초반 관객수 집중도와 주말/평일 간의 관객수 변동 패턴을 파악할 수 있습니다."
)


# [5. 구역 나누기 - 향후 그래프 추가용 구역]
st.write("---")
st.subheader("📊 추가 분석 (예정)")
st.write("📌 *이 구역에는 추후 새로운 분석 그래프가 추가될 예정입니다.*")
