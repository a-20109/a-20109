import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz

# 브라우저 탭 상단 설정
st.set_page_config(page_title="박스오피스 조회", page_icon="🍿")

# 한 번 불러온 데이터를 1시간(3600초) 동안 캐싱하여 불필요한 API 재호출 방지
@st.cache_data(ttl=3600)
def fetch_box_office(target_date, api_key):
    # 스트림릿 클라우드에서 SSLError 방지를 위해 https 대신 http 사용
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # 네트워크 연결 등 기본 오류 검사
        data = response.json()
        
        # 1. API 키 오류 등 KOBIS 서버에서 faultInfo를 내려주는 경우
        if "faultInfo" in data:
            return None, f"API 오류가 발생했습니다. 키 설정을 확인해 주세요. ({data['faultInfo'].get('message', '')})"
            
        # 2. 결과는 왔으나 데이터 목록이 비어 있는 경우 (집계 전)
        box_office_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        if not box_office_list:
            return None, "그날은 아직 집계 전입니다"
            
        return box_office_list, None
        
    except requests.exceptions.RequestException:
        return None, "서버와 연결할 수 없습니다. 인터넷 상태를 확인해 주세요."
    except Exception as e:
        return None, f"알 수 없는 오류가 발생했습니다: {e}"

def main():
    st.title("🍿 박스오피스 조회")
    
    # 한국 시간(KST) 기준 '어제' 계산
    kst = pytz.timezone('Asia/Seoul')
    today_kst = datetime.now(kst)
    yesterday_kst = today_kst - timedelta(days=1)
    
    # 달력 위젯 (기본 선택값과 최대 선택 가능 날짜를 '어제'로 제한)
    selected_date = st.date_input(
        "조회할 날짜를 선택하세요",
        value=yesterday_kst.date(),
        max_value=yesterday_kst.date()
    )
    
    # 선택된 날짜를 API 요청용 형식(YYYYMMDD)과 화면 표시용으로 변환
    target_dt = selected_date.strftime("%Y%m%d")
    display_dt = selected_date.strftime("%Y년 %m월 %d일")
    
    st.write(f"**조회 일자:** {display_dt}")
    
    # 스트림릿 클라우드의 비밀 금고(secrets)에서 KOBIS_KEY를 가져옴
    if "KOBIS_KEY" not in st.secrets:
        st.error("비밀 금고에 'KOBIS_KEY'가 없습니다. Streamlit Cloud 설정에서 추가해 주세요.")
        st.stop()
        
    api_key = st.secrets["KOBIS_KEY"]
    
    # 데이터 호출
    with st.spinner("데이터를 불러오는 중입니다..."):
        raw_data, error_msg = fetch_box_office(target_dt, api_key)
        
    # 데이터가 없거나 오류가 발생하면 안내 메시지 표시 후 아래 코드 실행 중단
    if error_msg:
        st.info(error_msg)
        st.stop()
        
    # JSON 리스트를 Pandas 데이터프레임으로 변환
    df = pd.DataFrame(raw_data)
    
    # 문자열로 들어온 숫자 데이터들을 계산과 정렬을 위해 숫자(Integer) 타입으로 변환
    numeric_cols = ['rank', 'rankInten', 'audiCnt', 'audiAcc', 'scrnCnt']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
        
    # 순위 증감(rankInten) 값을 화살표와 함께 표시하는 함수
    def format_rank_change(val):
        if val > 0:
            return f"🔺 {val}"
        elif val < 0:
            return f"🔽 {abs(val)}" # 음수인 경우 양수로 바꿔서 화살표 기호와 결합
        else:
            return "-"
            
    # 데이터프레임에 '순위 증감' 열 추가
    df['순위 증감'] = df['rankInten'].apply(format_rank_change)
    
    # 누적 관객수가 100만 명 이상인 영화 이름 옆에 트로피 이모지 추가
    df['movieNm'] = df.apply(
        lambda row: f"{row['movieNm']} 🏆" if row['audiAcc'] >= 1000000 else row['movieNm'], 
        axis=1
    )
    
    # 1위 영화 지표 카드 세팅
    st.subheader(f"🥇 1위: {df.loc[0, 'movieNm']}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("일일 관객수", f"{df.loc[0, 'audiCnt']:,}명")
    with col2:
        st.metric("누적 관객수", f"{df.loc[0, 'audiAcc']:,}명")
    with col3:
        st.metric("스크린수", f"{df.loc[0, 'scrnCnt']:,}개")
        
    st.markdown("---")
    
    # 상위 5편 막대그래프 세팅
    st.subheader("📊 관객수 상위 5편")
    # 영화명을 X축, 일일관객수를 Y축으로 설정하여 상위 5개 추출
    top5_df = df.head(5)[['movieNm', 'audiCnt']].set_index('movieNm')
    st.bar_chart(top5_df)
    
    st.markdown("---")
    
    # 전체 순위 표 세팅
    st.subheader("📋 전체 순위 (Top 10)")
    # 표에 표시할 열을 선택하고, 새로 만든 '순위 증감' 열도 포함
    table_df = df[['rank', '순위 증감', 'movieNm', 'openDt', 'audiCnt', 'audiAcc', 'scrnCnt']].copy()
    table_df.columns = ['순위', '순위 증감', '영화명', '개봉일', '관객수', '누적관객', '스크린수']
    
    # 인덱스 번호를 숨기고 표 출력
    st.dataframe(table_df, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
