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
    df['first_week_audi'] = df['first_week_audi'].fillna(0)
    df['nation'] = df['nation'].fillna('기타') # 국가 정보가 없는 경우 '기타'로 처리
    
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

fig3 = px.histogram(
    df, 
    x='total_audi',
    nbins=20,
    labels={'total_audi': '총 관객 수 (명)'}
)

fig3.update_traces(hovertemplate='총 관객 수 구간: %{x}<br>영화 편수: %{y}편<extra></extra>')
fig3.update_layout(yaxis_title="영화 편수 (편)")

st.plotly_chart(fig3, use_container_width=True)

# 자동으로 인사이트 문구 계산하기
max_movie = df.loc[df['total_audi'].idxmax(), 'movieNm']
max_audi = int(df['total_audi'].max())

bins = pd.cut(df['total_audi'], bins=20)
most_common_interval = bins.value_counts().idxmax()
min_val = max(0, int(most_common_interval.left)) 
max_val = int(most_common_interval.right)        

st.info(f"**💡 이 그래프로 알 수 있는 것**\n\n"
        f"대부분의 영화가 **{min_val:,}명 ~ {max_val:,}명** 구간에 몰려 있으며, "
        f"가장 관객이 많은 영화는 **'{max_movie}'**({max_audi:,}명)입니다.")

st.divider()

# ==========================================
# 7. 네 번째 그래프: 개봉일 스크린 수와 총 관객 수의 관계 (산점도)
# ==========================================
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계 (산점도)")

fig4 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',         
    hover_name='movieNm',  
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'genre': '장르'
    }
)

fig4.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<extra></extra>'
)

st.plotly_chart(fig4, use_container_width=True)

st.info("**💡 이 그래프로 알 수 있는 것**\n\n(이곳에 그래프를 보고 발견한 사실을 한 문장으로 적어주세요. 예: 개봉일 스크린 수가 많을수록 총 관객 수가 늘어나는 경향이 있는지 확인할 수 있습니다.)")

st.divider()

# ==========================================
# 8. 다섯 번째 그래프: 장르별 총 관객 수 분포 (상자 그림)
# ==========================================
st.subheader("5. 주요 장르별 총 관객 수 분포 (상자 그림)")

genre_counts_box = df['genre'].value_counts()
genres_over_10 = genre_counts_box[genre_counts_box >= 10].index
df_box = df[df['genre'].isin(genres_over_10)]

fig5 = px.box(
    df_box,
    x='genre',
    y='total_audi',
    hover_data=['movieNm'], 
    labels={
        'genre': '장르',
        'total_audi': '총 관객 수 (명)'
    }
)

st.plotly_chart(fig5, use_container_width=True)

st.info("**💡 이 그래프로 알 수 있는 것**\n\n(이곳에 그래프를 보고 발견한 사실을 한 문장으로 적어주세요. 예: 장르별 일반적인 관객 수의 범위와, 평균을 크게 웃도는 예외적인 흥행작(상자 밖의 점)을 확인할 수 있습니다.)")

st.divider()

# ==========================================
# 9. 여섯 번째 그래프: 스크린 수, 총 관객 수, 첫 주 관객 수 (버블 차트)
# ==========================================
st.subheader("6. 개봉일 스크린 수, 총 관객 수, 첫 주 관객 수 (버블 차트)")

fig6 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi', 
    color='genre',         
    hover_name='movieNm',
    hover_data={'first_week_audi': True, 'first_scrn': False, 'total_audi': False}, 
    size_max=50,             
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'first_week_audi': '개봉 첫 주 관객 (명)',
        'genre': '장르'
    }
)

fig6.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<br>첫 주 관객 수: %{customdata[0]:,.0f}명<extra></extra>'
)

st.plotly_chart(fig6, use_container_width=True)

st.info("**💡 이 그래프로 알 수 있는 것**\n\n(이곳에 그래프를 보고 발견한 사실을 한 문장으로 적어주세요. 예: 점의 위치뿐만 아니라 원의 크기를 통해 개봉 초반의 폭발력이 최종 흥행에 얼마나 기여했는지 유추해 볼 수 있습니다.)")

st.divider()

# ==========================================
# 10. 일곱 번째 그래프: 제작 국가 -> 장르 (선버스트 차트)
# ==========================================
st.subheader("7. 제작 국가 및 장르 분포 (선버스트 그래프)")

# 값이 지정되지 않으면 기본적으로 각 행(영화 1편)을 1로 세어 칸 크기를 결정합니다.
fig7 = px.sunburst(
    df,
    path=['nation', 'genre'], # 안쪽 원(국가)에서 바깥쪽 원(장르)으로 뻗어나감
)

fig7.update_traces(
    hovertemplate='<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>'
)

st.plotly_chart(fig7, use_container_width=True)

st.info("**💡 이 그래프로 알 수 있는 것**\n\n(이곳에 그래프를 보고 발견한 사실을 한 문장으로 적어주세요. 예: 한국 영화는 어떤 장르가 주를 이루고, 미국 영화는 어떤 장르가 많은지 한눈에 비교할 수 있습니다.)")

st.divider()
