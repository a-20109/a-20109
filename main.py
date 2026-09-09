import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz

# 브라우저 탭 상단 설정
st.set_page_config(page_title="어제의 박스오피스", page_icon="🍿")

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
            
        # 2. 결과는 왔으나 데이터 목록이 비어 있는 경우
        box_office_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        if not box_office_list:
            return None, "해당 날짜의 데이터가 아직 집계되지 않았거나 없습니다. 나중에 다시 시도해 주세요."
            
        return box_office_list, None
        
    except requests.exceptions.RequestException:
        return None, "서버와 연결할 수 없습니다. 인터넷 상태를 확인해 주세요."
    except Exception as e:
        return None, f"알 수 없는 오류가 발생했습니다: {e}"

def main():
    st.title("🍿 어제의 박스오피스")
    
    # 배포 서버의 시간이 다를 수 있으므로 명시적으로 한국 시간(KST) 기준 '어제'를 계산
    kst = pytz.timezone('Asia/Seoul')
    today_kst = datetime.now(kst)
    yesterday_kst = today_kst - timedelta(days=1)
    
    target_dt = yesterday_kst.strftime("%Y%m%d") # API 요청용 (예: 20231025)
    display_dt = yesterday_kst.strftime("%Y년 %m월 %d일") # 화면 표시용
    
    st.write(f"**조회 일자:** {display_dt}")
    
    # 스트림릿 클라우드의 비밀 금고(secrets)에서 KOBIS_KEY를 가져옴
    if "KOBIS_KEY" not in st.secrets:
        st.error("비밀 금고에 'KOBIS_KEY'가 없습니다. Streamlit Cloud 설정에서 추가해 주세요.")
        st.stop()
        
    api_key = st.secrets["KOBIS_KEY"]
    
    # 데이터 호출
    with st.spinner("데이터를 불러오는 중입니다..."):
        raw_data, error_msg = fetch_box_office(target_dt, api_key)
        
    # 오류 메시지가 있으면 화면에 띄우고 아래 코드 실행 중단
    if error_msg:
        st.error(error_msg)
        st.stop()
        
    # JSON 리스트를 다루기 쉽게 Pandas 데이터프레임으로 변환
    df = pd.DataFrame(raw_data)
    
    # API에서 넘어온 문자열(String) 타입의 숫자들을 실제 숫자(Integer) 타입으로 변환
    numeric_cols = ['rank', 'audiCnt', 'audiAcc', 'scrnCnt']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
        
    # 1위 영화 지표 카드 3장 세팅
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
    # 영화명을 X축(인덱스)으로, 일일관객수를 Y축으로 설정하여 5개만 추출
    top5_df = df.head(5)[['movieNm', 'audiCnt']].set_index('movieNm')
    st.bar_chart(top5_df)
    
    st.markdown("---")
    
    # 전체 순위 표 세팅
    st.subheader("📋 전체 순위 (Top 10)")
    # 표에 표시할 열만 골라서 한글 이름으로 변경
    table_df = df[['rank', 'movieNm', 'openDt', 'audiCnt', 'audiAcc', 'scrnCnt']].copy()
    table_df.columns = ['순위', '영화명', '개봉일', '관객수', '누적관객', '스크린수']
    
    # 왼쪽의 기본 인덱스(0, 1, 2...)를 숨기고 표 출력
    st.dataframe(table_df, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
