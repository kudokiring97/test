import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from data_loader import load_air_quality_data

# 데이터 로드 함수
def load_data(serial_no):
    df = load_air_quality_data(serial_no=serial_no)
    if df.empty:
        st.error("데이터가 없습니다.")
        return pd.DataFrame()
    df['DATE'] = pd.to_datetime(df['DATE'])
    return df

# 지수 변환 함수 (cipi 계산용)
def convert_to_score(value, ranges):
    # 오염물질 농도를 기준으로 점수를 변환합니다.
    if value <= ranges[0]:
        return 100
    elif value <= ranges[1]:
        return 90
    elif value <= ranges[2]:
        return 80
    elif value <= ranges[3]:
        return 50
    elif value <= ranges[4]:
        return 49
    else:
        return 0


# cipi 계산 함수
def calculate_cipi(pm25, pm10, co2, voc):
    # 오염 물질 별로 점수를 변환합니다.
    pm25_score = convert_to_score(pm25, [15, 35, 75, 150, 500])
    pm10_score = convert_to_score(pm10, [30, 80, 150, 300, 600])
    co2_score = convert_to_score(co2, [500, 1000, 1500, 2000, 5000])
    voc_score = convert_to_score(voc, [200, 400, 1000, 2000, 10000])
    
    # 가중치를 적용하여 cipi 계산
    weights = {'PM25': 0.2, 'PM10': 0.2, 'CO2': 0.4, 'VOC': 0.2}
    cipi = (
        pm25_score * weights['PM25'] + 
        pm10_score * weights['PM10'] + 
        co2_score * weights['CO2'] + 
        voc_score * weights['VOC']
    )
    return cipi

# CICI 지수 등급 함수
def get_cici_level(cici_score):
    if cici_score >= 90:
        return "매우 좋음", "😊", "#1E90FF"  # 파랑
    elif cici_score >= 70:
        return "좋음", "🙂", "#00BFFF"  # 하늘색
    elif cici_score >= 50:
        return "나쁨", "😐", "#FFD700"  # 노랑
    else:
        return "매우 나쁨", "😷", "#FF4500"  # 빨강

def render_detailed_view01():
    # 예시 데이터 로드
    serial_no = 'ICW0W2000041'
    df = load_data(serial_no)
    if df.empty:
        return

    # 오늘 날짜와 2주 전 날짜 설정
    today = datetime.now()
    two_weeks_ago = today - timedelta(weeks=2)

    # 데이터 필터링 (2주 전부터 오늘까지)
    filtered_df = df[(df['DATE'] >= two_weeks_ago) & (df['DATE'] <= today)]

    # 최신 데이터에서 cipi 계산
    latest_row = filtered_df.iloc[-1]
    cici_score = calculate_cipi(latest_row['PM25'], latest_row['PM10'], latest_row['CO2'], latest_row['VOC'])
    cici_level, emoji, color = get_cici_level(cici_score)

    if filtered_df.empty:
        st.warning("2주 이내의 데이터가 없습니다.")
        return

    # 제목 및 홈 버튼
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🔙 돌아가기"):
            st.session_state.page = "device1_dashboard"
            st.rerun()


    # 레이아웃 구성 (3:2 비율)
    left_col, right_col = st.columns([3, 2])

    # 좌측: 통합 실내 청정 지수 및 공식 표시
    with left_col:
        st.markdown("<h2 style='text-align: center;'>통합 실내 청정 지수(CIPI)</h2>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; font-size: 16px; margin-top: 10px;'>
            <b>*cipi = PM2.5 (20%) + PM10 (20%) + CO₂ (40%) + VOCs (20%)</b>
        </div>
        """, unsafe_allow_html=True)

    # 우측: cipi 점수 표시
    with right_col:
        st.markdown(f"<h2 style='text-align: center; color: {color};'>{emoji} {round(cici_score, 2)}</h2>", unsafe_allow_html=True)

   
    # 간격 추가
    st.markdown("<br><br>", unsafe_allow_html=True)
    # 각 그래프를 2열로 배치
    graph_titles = ["미세먼지 그래프", "초미세먼지 그래프", "CO₂ 그래프", "온도 그래프", "습도 그래프", "소음 그래프"]
    graph_columns = st.columns(3)
    graph_data = [
        ("PM10", "미세먼지 농도 (PM10)", "µg/m³"),
        ("PM25", "초미세먼지 농도 (PM2.5)", "µg/m³"),
        ("CO2", "이산화탄소 농도 (CO₂)", "ppm"),
        ("TEMP", "온도", "°C"),
        ("HUMI", "습도", "%"),
        ("VOC", "휘발성유기화합물질 (VOCs)", "ppb")
    ]

    # 그래프 생성 (높이 조정)
    for idx, (column, title, unit) in enumerate(graph_data):
        fig = px.line(filtered_df, x='DATE', y=column, title=title)
        fig.update_layout(
            yaxis_title=unit,
            xaxis_title="날짜",
            height=250  # 그래프 높이를 250으로 설정
        )
        
        with graph_columns[idx % 3]:  # 3열로 배치
            st.plotly_chart(fig, use_container_width=True)

