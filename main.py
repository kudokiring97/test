import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="Streamlit-Folium Demo",
    page_icon=":world_map:",
    layout="wide",
)

import folium
from streamlit_folium import st_folium
from device1_dashboard import render_device1_dashboard
from device2_dashboard import render_device2_dashboard
from device3_dashboard import render_device3_dashboard
from info01 import render_detailed_view01
from info02 import render_detailed_view02
from info03 import render_detailed_view03


# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state["page"] = "main"

# 핀 클릭 시 세션 상태 변경 함수 정의
def go_to_page(page_name):
    st.session_state["page"] = page_name

# 메인 페이지 렌더링 함수 정의
def render_main_page():
    st.title("용인외국어고등학교 공기질 측정 대시보드")


    # 지도의 중심 위치와 확대 레벨 설정 (zoom_start=18)
    map_center = [37.329786, 127.255688]
    m = folium.Map(location=map_center, zoom_start=18, tiles=None)  # 기본 타일을 제거

    # 위성 타일 추가
    folium.TileLayer('Esri.WorldImagery', name='위성지도').add_to(m)

    # 핀에 사용할 실제 이미지 URL과 위치 설정
    pins = [
        {
            "location": [37.330040, 127.255418],
            "tooltip": "LUX HALL",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
            "page": "device1_dashboard"
        },
        {
            "location": [37.330482, 127.256688],
            "tooltip": "ACE HALL",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
            "page": "device2_dashboard"
        },
        {
            "location": [37.329216, 127.255288],
            "tooltip": "야외 학습장",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
            "page": "device3_dashboard"
        }
    ]

    # 커스텀 핀 추가
    for pin in pins:
        icon = folium.CustomIcon(pin["icon_url"], icon_size=(30, 30))
        folium.Marker(
            location=pin["location"],
            tooltip=pin["tooltip"],
            icon=icon
        ).add_to(m)

    # Folium 지도를 Streamlit에 렌더링하고 상호작용 데이터 가져오기
    st_data = st_folium(m, width=1000, height=650)

    # 핀 클릭 상호작용 확인 및 페이지 이동
    if st_data is not None:
        if 'last_object_clicked' in st_data and st_data['last_object_clicked'] is not None:
            clicked_location = st_data['last_object_clicked']['lat'], st_data['last_object_clicked']['lng']
            for pin in pins:
                if (round(pin['location'][0], 5), round(pin['location'][1], 5)) == (round(clicked_location[0], 5), round(clicked_location[1], 5)):
                    go_to_page(pin['page'])
                    st.rerun()  # 페이지 새로고침
        else:
            st.write("No location clicked")
    else:
        st.write("No interaction data")


# 페이지 전환 로직
if "page" not in st.session_state:
    st.session_state["page"] = "main"  # 기본 페이지 설정

# 페이지 상태에 따른 렌더링
if st.session_state["page"] == "main":
    render_main_page()
elif st.session_state["page"] == "device1_dashboard":
    render_device1_dashboard()
elif st.session_state["page"] == "device2_dashboard":
    render_device2_dashboard()
elif st.session_state["page"] == "device3_dashboard":
    render_device3_dashboard()
elif st.session_state.page == "detailed_view01":
    render_detailed_view01()
elif st.session_state.page == "detailed_view02":
    render_detailed_view02()
elif st.session_state.page == "detailed_view03":
    render_detailed_view03()
