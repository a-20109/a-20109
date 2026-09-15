import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(page_title="영화 데이터 그래프 도감 2", layout="wide")

# 2. 메인 제목
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

# 3. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 전처리: '|' 기호로 구분된 경우 첫 번째 장르만 추출
    df['genre'] = df['genre'].astype(str).str.split('|').str[0]
    
    # 결측치 처리
    df['total_audi'] = df['total_audi'].fillna(0)
    
    return df

df = load_data()

st.divider() 

# ==========================================
# 4. 첫 번째 그래프: 장르별 영화 편수 (도넛 그래프)
# ==========================================
st.subheader("1. 장르별 영화 편수 분포")

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '편수']

fig1 = px.pie(
    genre_counts,
    names='장르',
    values='편수',
    hole=0.4, 
)

fig1.update_traces(hovertemplate='<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>')
st.plotly_chart(fig1, use_container_width=True)

st.info("**💡 이 그래프로 알 수 있는 것**\n\n(이곳에 그래프를 보고 발견한 사실을 한 문장으로 적어주세요.)")

st.divider() 

# ==========================================
# 5. 두 번째 그래프: 장르 및 영화별 총 관객 수 (트리맵)
# ==========================================
st.subheader("2. 장르별 총 관객 수와 흥행작 (트리맵)")

fig2 = px.treemap(
    df,
    path=['genre', 'movieNm'], 
    values='total_audi',       
)

fig2.update_traces(
    hovertemplate='<b>%{label}</b><br>총 관객: %{value:,.0f}명<extra></extra>'
)
st.plotly_chart(fig2, use_container_width=True)

st.info("**💡 이 그래프로 알 수 있는 것**\n\n(이곳에 그래프를 보고 발견한 사실을 한 문장으로 적어주세요.)")

st.divider() 

# ==========================================
# 6. 세 번째 그래프: 총 관객 수 분포 (히스토그램)
# ==========================================
st.subheader("3. 총 관객 수 분포 (히스토그램)")

# 히스토그램 생성 (20개 구간으로 나눔)
fig3 = px.histogram(
    df, 
    x='total_audi',
    nbins=20,
    labels={'total_audi': '총 관객 수 (명)'}
)

# 툴팁과 축 레이블 설정
fig3.update_traces(hovertemplate='총 관객 수 구간: %{x}<br>영화 편수: %{y}편<extra></extra>')
fig3.update_layout(yaxis_title="영화 편수 (편)")

st.plotly_chart(fig3, use_container_width=True)

# 자동으로 인사이트 문구 계산하기
max_movie = df.loc[df['total_audi'].idxmax(), 'movieNm']
max_audi = int(df['total_audi'].max())

# 데이터를 20개 구간으로 나누어 가장 영화가 많은 구간 찾기
bins = pd.cut(df['total_audi'], bins=20)
most_common_interval = bins.value_counts().idxmax()
min_val = max(0, int(most_common_interval.left)) # 구간 시작점 (음수 방지)
max_val = int(most_common_interval.right)        # 구간 끝점

# 그래프 해석 구역 (계산된 결과 출력)
st.info(f"**💡 이 그래프로 알 수 있는 것**\n\n"
        f"대부분의 영화가 **{min_val:,}명 ~ {max_val:,}명** 구간에 몰려 있으며, "
        f"가장 관객이 많은 영화는 **'{max_movie}'**({max_audi:,}명)입니다.")

st.divider()
