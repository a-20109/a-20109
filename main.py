# main.py
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
    
    # 결측치 처리 (트리맵, 버블 차트 등의 오류 방지)
    df['total_audi'] = df['total_audi'].fillna(0)
    df['first_week_audi'] = df['first_week_audi'].fillna(0)
    
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
    size='first_week_audi',  # 버블의 크기를 첫 주 관객 수로 지정
    color='genre',         
    hover_name='movieNm',
    hover_data={'first_week_audi': True, 'first_scrn': False, 'total_audi': False}, 
    size_max=50,             # 가장 큰 버블의 최대 크기 설정
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'first_week_audi': '개봉 첫 주 관객 (명)',
        'genre': '장르'
    }
)

# 툴팁에 세 가지 정보를 모두 천 단위 콤마로 표시되도록 세팅
fig6.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<br>첫 주 관객 수: %{customdata[0]:,.0f}명<extra></extra>'
)

st.plotly_chart(fig6, use_container_width=True)

st.info("**💡 이 그래프로 알 수 있는 것**\n\n(이곳에 그래프를 보고 발견한 사실을 한 문장으로 적어주세요. 예: 점의 위치뿐만 아니라 원의 크기를 통해 개봉 초반의 폭발력이 최종 흥행에 얼마나 기여했는지 유추해 볼 수 있습니다.)")

st.divider()
```eof

여섯 번째 그래프까지 모두 완성되었습니다! 코드를 덮어쓰고 저장하신 후 새로고침하시면, 산점도의 점 크기가 개봉 첫 주 관객 수에 따라 커지는 버블 차트를 확인하실 수 있습니다.좋습니다! 네 번째 산점도를 바탕으로, 점의 크기를 첫 주 관객 수(`first_week_audi`)로 설정한 여섯 번째 **버블 그래프**를 그리는 파이썬(Python) 코드입니다. 

제가 직접 화면에 그래프를 띄워드릴 수는 없지만, 기존에 작업하시던 환경(Jupyter Notebook 등)에 아래 코드를 추가해서 실행하시면 멋진 버블 그래프가 완성될 거예요.

## 여섯 번째 그래프: 첫 주 관객 수 버블 그래프

기존 산점도 코드에서 `s` (사이즈) 속성이나 `size` 파라미터를 추가하면 간단하게 버블 그래프로 변환할 수 있습니다. 관객 수 데이터가 너무 크면 버블이 화면을 다 가릴 수 있으니, 적절한 비율로 축소해 주는 것이 포인트입니다.

### Seaborn을 사용하는 경우
```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))

# x와 y에는 네 번째 그래프에서 사용하신 컬럼명을 그대로 넣어주세요.
# sizes=(최소 크기, 최대 크기)를 조절하여 버블이 겹치지 않게 만듭니다.
sns.scatterplot(
    data=df, 
    x='x_column',       # 기존 x축 데이터 컬럼명
    y='y_column',       # 기존 y축 데이터 컬럼명
    size='first_week_audi', 
    sizes=(20, 500),    # 버블 크기 범위 지정
    alpha=0.6,          # 겹칠 때 잘 보이도록 투명도 조절
    color='royalblue'
)

plt.title('여섯 번째 그래프: 첫 주 관객 수(first_week_audi)에 따른 버블 그래프', fontsize=14)
plt.xlabel('X축 이름')
plt.ylabel('Y축 이름')

# 범례 위치 조정 (버블 크기 범례가 밖으로 나오도록)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
