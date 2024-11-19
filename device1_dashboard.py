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

def get_cipi_level(cipi):
    if cipi >= 90:
        level = "매우 좋음"
        emoji = "😊"
        description = """
        <div style='text-align: center;'>
            <h3>현재 실내 공기 상태는 매우 좋습니다.</h3>
            <p>초미세먼지와 이산화탄소 농도가 모두 최적 수준을 유지하고 있어 건강에 좋은 상태입니다.<br> 공기 청정기나 환기 시스템을 현재 상태로 유지하세요.</p>
        </div>
        """
    elif cipi >= 80:
        level = "좋음"
        emoji = "🙂"
        description = """
        <div style='text-align: center;'>
            <h3>실내 공기 상태가 좋습니다.</h3>
            <p>초미세먼지와 이산화탄소 농도가 기준치를 잘 유지하고 있어 쾌적한 환경이 지속되고 있습니다.<br>환기를 하루 2~3회 가볍게 실시해주시고, 공기 청정기 사용을 추천합니다.</p>
        </div>
        """
    elif cipi >= 50:
        level = "나쁨"
        emoji = "😐"
        description = """
        <div style='text-align: center;'>
            <h3>현재 실내 공기 상태가 좋지 않습니다.</h3>
            <p>초미세먼지와 이산화탄소 농도가 기준을 초과해 호흡기 건강에 영향을 줄 수 있습니다.<br>즉시 환기를 실시하고, 공기 청정기와 CO₂ 저감 장치를 활용해 공기 질을 개선하세요.<br> 가능하다면 실내 인원을 줄이고 공기 유동성을 확보하세요.</p>
        </div>
        """
    else:
        level = "매우 나쁨"
        emoji = "😷"
        description = """
        <div style='text-align: center;'>
            <h3>실내 공기 상태가 매우 나쁩니다.</h3>
            <p>초미세먼지와 이산화탄소 농도가 높은 수준으로 건강에 심각한 영향을 줄 수 있습니다.<br>즉시 창문을 열어 충분히 환기하고, 공기 청정기를 최대로 가동하세요.<br>실내 인원 수를 줄이고 필요한 경우 마스크를 착용하는 것도 도움이 됩니다.</p>
        </div>
        """
    
    return level, emoji, description


# 대시보드 UI 구성
def render_device1_dashboard():
    serial_no = 'ICW0W2000041'
    df = load_data(serial_no)
    if df.empty:
        return

    # 대시보드 화면 분할
    left_col, right_col = st.columns([3, 2], gap='large')

    # 좌측 화면 (실시간 상태, 데이터, 날짜 선택)
    with left_col:
        # 제목 및 홈 버튼
        col1, col2 = st.columns([8, 2])
        with col1:
            st.markdown("<h1 style='text-align: left;'>LUX HALL</h1>", unsafe_allow_html=True)
        with col2:
            if st.button("🏠 홈으로"):
                st.session_state.page = "main"
                st.rerun()


        # 실시간 CIPI 상태 표시
        st.markdown("<h3 style='color: #007BFF;'>👨‍🏫 종합 리포트</h3>", unsafe_allow_html=True)
        if not df.empty:
            latest_pm25 = df['PM25'].iloc[-1]
            latest_pm10 = df['PM10'].iloc[-1]
            latest_co2 = df['CO2'].iloc[-1]
            latest_voc = df['VOC'].iloc[-1]
            
            cipi = calculate_cipi(latest_pm25, latest_pm10, latest_co2, latest_voc)
            # get_cipi_level 함수 호출 시 세 개의 변수를 할당
            cipi_level, emoji, cipi_description = get_cipi_level(cipi)

            st.markdown(f"<h2 style='text-align: center; color: #FF4500;'>{cipi_level} {emoji}</h2>", unsafe_allow_html=True)
            st.markdown(cipi_description, unsafe_allow_html=True)
        
        # 자세히 보기 버튼
        if st.button("🔍 자세히 보기"):
            st.session_state.page = "detailed_view01"
            st.rerun()

        # 간격 추가
        st.markdown("<br><br>", unsafe_allow_html=True)


        # 실시간 데이터 표시
        st.markdown("<h3 style='color: #007BFF;'>📊 실시간 데이터</h3>", unsafe_allow_html=True)
        
        # 간격 추가
        st.markdown("<br><br>", unsafe_allow_html=True)

        pm25_col, pm10_col, co2_col = st.columns(3)
        pm25_col.metric("초미세먼지 (PM2.5)", f"{latest_pm25} µg/m³")
        pm10_col.metric("미세먼지 (PM10)", f"{latest_pm10} µg/m³")
        co2_col.metric("이산화탄소 (CO2)", f"{latest_co2} ppm")

        

    # 우측 화면 (그래프 시각화)
    with right_col:
        # 날짜 선택 위젯
        min_date = df['DATE'].min().date()
        max_date = df['DATE'].max().date()
        today = datetime.today().date()

        if "selected_dates" not in st.session_state:
            st.session_state.selected_dates = (today - timedelta(days=1), today)
        elif "selected_dates" in st.session_state:
            st.session_state.selected_dates = (max_date - timedelta(days=1), max_date)

        selected_range = st.date_input(
            "📅집계 기간 선택",
            value=(st.session_state.selected_dates[0], st.session_state.selected_dates[1]),
            min_value=min_date,
            max_value=max_date
        )

        filtered_df = df[(df['DATE'] >= pd.to_datetime(selected_range[0])) &
                         (df['DATE'] <= pd.to_datetime(selected_range[1]))]    

        fig_pm10 = px.line(filtered_df, x='DATE', y='PM10', title='미세먼지 농도 변화', markers=True)
        fig_co2 = px.line(filtered_df, x='DATE', y='CO2', title='CO2 농도 변화', markers=True)
        
        fig_pm10.update_layout(height=300)  # 높이 조정
        fig_co2.update_layout(height=300)  # 높이 조정

        st.plotly_chart(fig_pm10, use_container_width=True)
        st.plotly_chart(fig_co2, use_container_width=True)

# # 페이지 상태에 따른 화면 렌더링
# if st.session_state["page"] == "dashboard":
#     render_device1_dashboard()
# elif st.session_state["page"] == "detailed_view":
#     render_detailed_view()  # info01.py에서 정의된 함수 호출