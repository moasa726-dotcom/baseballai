import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="FM 유소년 야구단 디렉터 허브",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 스타일링 (CSS) ---
st.markdown(
    """
    <style>
    .stApp { background-color: #121417; color: #E2E8F0; }
    .fm-card {
        background-color: #1A1F26;
        border: 1px solid #2D3748;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 12px;
    }
    .fm-card-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #A0AEC0;
        margin-bottom: 10px;
        font-weight: 700;
        border-bottom: 1px solid #2D3748;
        padding-bottom: 5px;
    }
    .attr-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 8px;
        background: #14181E;
        border-radius: 4px;
        margin-bottom: 6px;
        border-left: 3px solid #4A5568;
    }
    .attr-val {
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        text-align: center;
        min-width: 34px;
    }
    .val-elite { background-color: #15803D; color: #F0FDF4; border-left-color: #22C55E !important; }
    .val-good  { background-color: #3F6212; color: #ECFCCB; border-left-color: #84CC16 !important; }
    .val-avg   { background-color: #B45309; color: #FFFBEB; border-left-color: #F59E0B !important; }
    .val-poor  { background-color: #991B1B; color: #FEF2F2; border-left-color: #EF4444 !important; }
    .pro-tag   { color: #4ADE80; font-weight: 600; }
    .con-tag   { color: #F87171; font-weight: 600; }
    
    /* 벤치 선수 스타일 */
    .bench-player {
        display: inline-block;
        background-color: #2D3748;
        color: #E2E8F0;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 3px;
        font-size: 0.8rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 데이터베이스 버전 업그레이드 (나이, 성별 추가)
DB_FILE = "team_player_history_kr_v3.csv"
VALID_POSITIONS = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]

# --- 데이터 로드 및 초기화 ---
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # 날짜 컬럼 형식 통일
        df['GameDate'] = pd.to_datetime(df['GameDate']).dt.strftime('%Y-%m-%d')
        # 혹시 모를 None 값 처리 (스크린샷 문제 해결)
        df = df.dropna(subset=['PlayerName'])
        return df
    else:
        # 새로운 데이터 구조: 'MainPosition'(주 포지션), 'Age', 'Gender' 컬럼 추가
        starter_df = pd.DataFrame({
            "PlayerName": ["김용준", "김용준", "박민수", "박민수", "이도윤", "이도윤", "최주원", "허이레"],
            "GameDate": ["2026-05-01", "2026-05-08", "2026-05-01", "2026-05-08", "2026-05-01", "2026-05-08", "2026-05-08", "2026-05-08"],
            "AgeGroup": ["14-15세", "14-15세", "12-13세", "12-13세", "9-11세", "9-11세", "14-15세", "12-13세"],
            "Age": [15, 15, 13, 13, 10, 10, 14, 12],
            "Gender": ["남", "남", "남", "남", "남", "남", "남", "남"],
            "MainPosition": ["1B", "1B", "SS", "SS", "P", "P", "CF", "C"],
            "Role": ["타자", "타자", "타자", "타자", "투수", "투수", "타자", "포수"],
            "PlayedPosition": ["1B", "1B", "SS", "2B", "P", "P", "CF", "C"],
            "PA": [4, 3, 4, 4, 0, 0, 4, 3], "AB": [3, 3, 3, 4, 0, 0, 4, 2],
            "H": [1, 2, 0, 1, 0, 0, 2, 1], "BB": [1, 0, 1, 0, 1, 1, 0, 1],
            "K": [1, 0, 2, 1, 3, 2, 0, 1], "TB": [1, 3, 0, 1, 0, 0, 4, 1],
            "Errors": [0, 0, 1, 0, 0, 0, 0, 0],
            "HighZone_Whiffs": [2, 0, 4, 2, 0, 0, 0, 1], "MidZone_Whiffs": [0, 1, 1, 1, 0, 0, 0, 0],
            "LowZone_Whiffs": [1, 0, 3, 2, 0, 0, 1, 0], "Chase_Zone10": [1, 0, 3, 2, 0, 0, 0, 1],
            "PitchesThrown": [0, 0, 0, 0, 45, 50, 0, 0], "Strikes": [0, 0, 0, 0, 29, 33, 0, 0],
            "IP_Outs": [0, 0, 0, 0, 6, 6, 0, 0], "ER": [0, 0, 0, 0, 1, 2, 0, 0],
            "WildPitches": [0, 0, 0, 0, 0, 1, 0, 0], "PassedBalls": [0, 0, 0, 0, 0, 0, 0, 0],
            "WildPitchesBlocked": [0, 0, 0, 0, 0, 0, 0, 2], "StealAttempts": [0, 0, 0, 0, 0, 0, 0, 2],
            "CaughtStealing": [0, 0, 0, 0, 0, 0, 0, 1], "ThrowingErrors": [0, 0, 0, 0, 0, 0, 0, 0],
        })
        starter_df.to_csv(DB_FILE, index=False)
        return starter_df

# 세션 상태에 데이터 저장
if 'df_history' not in st.session_state:
    st.session_state['df_history'] = load_data()

df_history = st.session_state['df_history']

# --- 공통 함수 ---
def save_data():
    st.session_state['df_history'].to_csv(DB_FILE, index=False)

def fm_color_class(val):
    if val >= 15: return "val-elite"
    elif val >= 11: return "val-good"
    elif val >= 7: return "val-avg"
    else: return "val-poor"

# 데이터베이스에서 고유 선수 목록 가져오기 함수 (갱신용)
def get_unique_players():
    if not st.session_state['df_history'].empty:
        # None 값을 제외하고 유효한 이름만 정렬하여 가져옴
        valid_df = st.session_state['df_history'].dropna(subset=['PlayerName'])
        return sorted(valid_df["PlayerName"].unique())
    return []

# ==========================================
# 사이드바: 데이터 수집 및 수동 추가
# ==========================================
st.sidebar.header("⚽ 데이터 수집 및 입력")

# 1. CSV 업로드
uploaded_file = st.sidebar.file_uploader("새 경기 CSV 업로드", type=["csv"])
if uploaded_file is not None:
    try:
        new_data = pd.read_csv(uploaded_file)
        st.session_state['df_history'] = pd.concat([st.session_state['df_history'], new_data], ignore_index=True)
        save_data()
        st.sidebar.success("새 경기 스탯이 병합되었습니다!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"CSV 로드 오류: {e}")

# 2. 직접 수동 입력 (로스터 연동)
with st.sidebar.expander("➕ 수동 경기 기록 추가", expanded=False):
    # 등록된 선수 목록 가져오기
    registered_players = get_unique_players()
    
    if not registered_players:
        st.warning("먼저 '로스터 및 포지션 관리' 탭에서 선수를 등록해주세요.")
    else:
        with st.form("manual_entry_form"):
            # 선수 이름: 로스터 기반 드롭다운으로 변경
            m_player = st.selectbox("선수 선택", registered_players)
            m_date = st.date_input("경기 날짜", datetime.now())
            
            # 선택한 선수의 최근 정보 가져오기 (연령대 자동 설정을 위해)
            player_info = st.session_state['df_history'][st.session_state['df_history']["PlayerName"] == m_player].iloc[-1]
            
            # 연령대, 나이, 성별, 주 포지션은 기존 데이터 기반으로 자동 입력 (비활성화)
            st.text_input("연령대", value=player_info["AgeGroup"], disabled=True)
            m_main_pos = st.text_input("주 포지션", value=player_info["MainPosition"], disabled=True)
            
            # 실제 출전 포지션 및 역할 선택
            col_played_pos, col_role = st.columns(2)
            m_played_pos = col_played_pos.selectbox("실제 출전 포지션", VALID_POSITIONS, index=VALID_POSITIONS.index(player_info["MainPosition"]))
            m_role = col_role.selectbox("역할", ["타자", "투수", "포수"])

            st.markdown("**기본 경기 기록**")
            col_pa, col_ab, col_h = st.columns(3)
            m_pa = col_pa.number_input("타석", 0, 20, 0)
            m_ab = col_ab.number_input("타수", 0, 20, 0)
            m_h = col_h.number_input("안타", 0, 20, 0)
            
            col_bb, col_k, col_tb = st.columns(3)
            m_bb = col_bb.number_input("볼넷", 0, 20, 0)
            m_k = col_k.number_input("삼진", 0, 20, 0)
            m_tb = col_tb.number_input("루타수", 0, 30, 0)
            
            m_err = st.number_input("실책", 0, 10, 0)

            # 역할별 상세 기록 입력은 복잡성을 줄이기 위해 생략 (필요시 추가 가능)

            submitted = st.form_submit_button("기록 저장")
            if submitted:
                # 자동 입력된 값들 가져오기
                m_age_group = player_info["AgeGroup"]
                m_age = player_info["Age"]
                m_gender = player_info["Gender"]

                new_row = {
                    "PlayerName": m_player, "GameDate": m_date.strftime('%Y-%m-%d'), 
                    "AgeGroup": m_age_group, "Age": m_age, "Gender": m_gender,
                    "MainPosition": m_main_pos, "Role": m_role, "PlayedPosition": m_played_pos,
                    "PA": m_pa, "AB": m_ab, "H": m_h, "BB": m_bb, "K": m_k, "TB": m_tb, "Errors": m_err,
                    "HighZone_Whiffs": 0, "MidZone_Whiffs": 0, "LowZone_Whiffs": 0, "Chase_Zone10": 0,
                    "PitchesThrown": 0, "Strikes": 0, "IP_Outs": 0, "ER": 0, "WildPitches": 0, 
                    "PassedBalls": 0, "WildPitchesBlocked": 0, "StealAttempts": 0, 
                    "CaughtStealing": 0, "ThrowingErrors": 0,
                }
                st.session_state['df_history'] = pd.concat([st.session_state['df_history'], pd.DataFrame([new_row])], ignore_index=True)
                save_data()
                st.sidebar.success(f"{m_player} 선수의 {m_date.strftime('%m/%d')} 경기 기록이 추가되었습니다!")
                st.rerun()

st.sidebar.download_button(
    label="전체 데이터 CSV 다운로드",
    data=df_history.to_csv(index=False),
    file_name="team_player_history_kr_v3_all.csv",
    mime="text/csv",
)

# ==========================================
# 메인 화면: 탭 구성
# ==========================================
tabs = st.tabs(["📊 선수단 종합", "🛡️ 수비/포지션", "👤 개인 프로필", "🛠️ 경기 기록 수정/삭제", "📋 AI 선발 라인업 추천", "👥 로스터 및 포지션 관리"])

# [cite: 탭 1, 2는 이전 코드 유지]
with tabs[0]: st.write("선수단 종합 비교 화면 (이전 코드)")
with tabs[1]: st.write("수비/포지션 분석 화면 (이전 코드)")

# ==========================================
# 탭 3: 개인 프로필 (오류 수정 및 박스 제거)
# ==========================================
with tabs[2]:
    # 등록된 선수 목록 가져오기
    registered_players = get_unique_players()
    
    if not registered_players:
        st.warning("로스터에 선수가 없습니다. '로스터 및 포지션 관리' 탭에서 선수를 등록해주세요.")
    else:
        selected_player = st.selectbox("🔍 프로필 조회할 선수 선택:", registered_players)

        player_df = df_history[df_history["PlayerName"] == selected_player].sort_values(by="GameDate")
        # 최근 기록 기반 정보
        player_info = player_df.iloc[-1]
        latest_tier = player_info["AgeGroup"]
        player_role = player_info["Role"]
        player_main_pos = player_info["MainPosition"]
        # 나이, 성별 추가 정보
        player_age = player_info["Age"]
        player_gender = player_info["Gender"]

        # 타자 계산
        total_PA = player_df["PA"].sum()
        total_AB = player_df["AB"].sum()
        total_H = player_df["H"].sum()
        total_BB = player_df["BB"].sum()
        total_K = player_df["K"].sum()
        total_TB = player_df["TB"].sum()
        total_Errors = player_df["Errors"].sum()

        avg = total_H / total_AB if total_AB > 0 else 0.0
        obp = ((total_H + total_BB) / (total_AB + total_BB)) if (total_AB + total_BB) > 0 else 0.0
        slg = total_TB / total_AB if total_AB > 0 else 0.0
        ops = obp + slg
        k_rate = total_K / total_PA if total_PA > 0 else 0.0

        # 투수 계산
        total_pitches = player_df["PitchesThrown"].sum()
        total_strikes = player_df["Strikes"].sum()
        strike_pct = (total_strikes / total_pitches) * 100 if total_pitches > 0 else 0.0
        total_ip_outs = player_df["IP_Outs"].sum()
        ip_display = f"{total_ip_outs // 3}.{total_ip_outs % 3}"
        pitcher_k = player_df["K"].sum()
        pitcher_bb = player_df["BB"].sum()

        # 포수 계산
        passed_balls = player_df["PassedBalls"].sum()
        blocked_balls = player_df["WildPitchesBlocked"].sum()
        cs_attempts = player_df["StealAttempts"].sum()
        cs_caught = player_df["CaughtStealing"].sum()
        catcher_errors = player_df["ThrowingErrors"].sum()

        # --- 상단 헤더 배너 (팀 내 역할 박스 제거) ---
        with st.container():
            st.caption(f"로스터 프로필 • {latest_tier} • {player_age}세/{player_gender} • 주 포지션: {player_main_pos} ({player_role})")
            st.title(selected_player)

            if player_role == "타자":
                st.markdown(f"**OPS:** `{ops:.3f}` &nbsp;|&nbsp; **타율:** `{avg:.3f}` &nbsp;|&nbsp; **삼진율(K%):** `{k_rate*100:.1f}%`")
            elif player_role == "투수":
                st.markdown(f"**이닝:** `{ip_display}` &nbsp;|&nbsp; **스트라이크 %:** `{strike_pct:.1f}%` &nbsp;|&nbsp; **탈삼진:** `{pitcher_k}` &nbsp;|&nbsp; **볼넷:** `{pitcher_bb}`")
            else:
                st.markdown(f"**블로킹 성공:** `{blocked_balls}` &nbsp;|&nbsp; **포일:** `{passed_balls}` &nbsp;|&nbsp; **도루저지:** `{cs_caught}/{cs_attempts}`")

        st.markdown("---")

        # --- 능력치, 코치 리포트, 존 포커스 ---
        col_attr, col_report, col_zone = st.columns([1.1, 1, 1])

        with col_attr:
            st.markdown('<div class="fm-card"><div class="fm-card-title">📊 기술 및 멘탈 능력치 (1-20 스케일)</div>', unsafe_allow_html=True)

            if player_role == "타자":
                attr_contact = max(1, min(20, round(avg * 40)))
                attr_power = max(1, min(20, round(slg * 25)))
                attr_vision = max(1, min(20, round((1.0 - k_rate) * 20)))
                attr_discipline = max(1, min(20, round((total_BB / max(1, total_PA)) * 45 + 5)))
                attr_defense = max(1, min(20, 20 - (total_Errors * 3)))
                attr_composure = max(1, min(20, round(obp * 22)))

                attributes = [
                    ("컨택 (배트 컨트롤)", attr_contact),
                    ("파워 (장타력)", attr_power),
                    ("선구안 (비전)", attr_vision),
                    ("타석 인내심", attr_discipline),
                    ("수비 안정감", attr_defense),
                    ("멘탈 (카운트 싸움)", attr_composure),
                ]
            elif player_role == "투수":
                attr_command = max(1, min(20, round(strike_pct / 4.5)))
                attr_control = max(1, min(20, 20 - pitcher_bb * 2))
                attr_stuff = max(1, min(20, round((pitcher_k / max(1, total_ip_outs)) * 12)))
                attr_stamina = max(1, min(20, round(total_pitches / 5)))
                attr_composure = max(1, min(20, 20 - player_df["WildPitches"].sum() * 3))

                attributes = [
                    ("커맨드 (스트라이크 비율)", attr_command),
                    ("제구력 (볼넷 억제)", attr_control),
                    ("구위 (탈삼진 능력)", attr_stuff),
                    ("스태미나 (투구 체력)", attr_stamina),
                    ("마운드 멘탈", attr_composure),
                ]
            else: # 포수
                attr_blocking = max(1, min(20, round((blocked_balls - passed_balls) * 3 + 12)))
                attr_arm_strength = max(1, min(20, round((cs_caught / max(1, cs_attempts)) * 20)))
                attr_accuracy = max(1, min(20, 20 - catcher_errors * 4))
                attr_game_mgmt = max(1, min(20, 15))

                attributes = [
                    ("블로킹 및 포구", attr_blocking),
                    ("어깨 (도루저지 능력)", attr_arm_strength),
                    ("송구 정확도", attr_accuracy),
                    ("게임 운영 및 BQ", attr_game_mgmt),
                ]

            for name, val in attributes:
                c_class = fm_color_class(val)
                st.markdown(
                    f"""
                    <div class="attr-row {c_class}">
                        <span style="font-weight: 500; color: #F1F5F9;">{name}</span>
                        <!-- 달러 싸인($) 제거 수정 완료 -->
                        <span class="attr-val {c_class}">{val}</span>
                    </div>
                    """, unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # [cite: 코치 리포트, 존 분석 탭은 이전 코드 유지]
        with col_report: st.write("코치 리포트 화면 (이전 코드)")
        with col_zone: st.write("존 분석 및 모니터링 화면 (이전 코드)")

        # [cite: 훈련 추천, 내보내기 탭은 이전 코드 유지]
        st.write("주간 훈련 추천 화면 (이전 코드)")
        st.write("맞춤형 데이터 내보내기 화면 (이전 코드)")

# ==========================================
# 탭 4: 경기 기록 수정/삭제 (드롭다운 개선)
# ==========================================
with tabs[3]:
    st.markdown("### 🛠️ 이전에 올렸던 경기 기록 수정 및 삭제")
    st.markdown("아래 표에서 직접 데이터를 수정하거나 행을 삭제할 수 있습니다. 변경 후 반드시 **'변경 사항 저장'** 버튼을 눌러주세요.")
    
    # 등록된 선수 목록 가져오기
    registered_players = get_unique_players()

    if not registered_players:
        st.warning("데이터가 없습니다.")
    else:
        # st.data_editor를 사용하여 데이터 편집 인터페이스 제공
        edited_df = st.data_editor(
            st.session_state['df_history'],
            key="history_editor",
            num_rows="dynamic", # 행 추가/삭제 가능
            use_container_width=True,
            # 주요 컬럼들 드롭다운 설정
            column_config={
                # 요청 사항: 선수 이름 드롭다운 메뉴로 변경
                "PlayerName": st.column_config.SelectboxColumn("선수 이름", options=registered_players, required=True),
                
                "GameDate": st.column_config.DateColumn("경기 날짜", format="YYYY-MM-DD", required=True),
                "AgeGroup": st.column_config.SelectboxColumn("연령대 그룹", options=["9-11세", "12-13세", "14-15세"]),
                # 나이, 성별 수정 가능 컬럼으로 표시
                "Age": st.column_config.NumberColumn("나이", min_value=7, max_value=16, step=1),
                "Gender": st.column_config.SelectboxColumn("성별", options=["남", "여"]),

                # 요청 사항: 포지션 드롭다운 메뉴로 변경
                "MainPosition": st.column_config.SelectboxColumn("주 포지션", options=VALID_POSITIONS),
                "PlayedPosition": st.column_config.SelectboxColumn("실제 출전 포지션", options=VALID_POSITIONS),
                
                "Role": st.column_config.SelectboxColumn("역할", options=["타자", "투수", "포수"]),
            }
        )

        col_save, col_reset = st.columns([1, 5])
        
        if col_save.button("📝 변경 사항 저장", type="primary"):
            # 편집된 데이터 세션 상태에 반영 및 파일 저장
            # 혹시 모를 None 값 제외 (스크린샷 문제 해결)
            cleaned_df = edited_df.dropna(subset=['PlayerName'])
            st.session_state['df_history'] = cleaned_df
            save_data()
            st.success("데이터베이스가 성공적으로 업데이트되었습니다!")
            st.rerun()
            
        if col_reset.button("🔄 되돌리기"):
            st.rerun() # 저장하지 않고 세션 상태 초기화

# ==========================================
# 탭 5: AI 선발 라인업 추천 (이전 코드 유지)
# ==========================================
with tabs[4]: st.write("AI 선발 라인업 추천 화면 (이전 코드)")

# ==========================================
# 탭 6: 로스터 및 포지션 관리 (신규 추가 요청 기능)
# ==========================================
with tabs[5]:
    st.markdown("### 👥 선수단 로스터 및 기본 정보 관리")
    st.markdown("여기에서 팀의 선수를 새로 등록하거나 기존 선수의 나이, 성별, 주 포지션 등 기본 정보를 관리합니다.")
    st.markdown("이 탭에서 관리하는 선수 목록은 다른 입력 탭의 드롭다운 메뉴에 자동으로 반영됩니다.")

    # 선수단 기본 정보 요약 표 생성 (최근 기록 기반)
    # 혹시 모를 None 값 제외 (스크린샷 문제 해결)
    valid_history = st.session_state['df_history'].dropna(subset=['PlayerName'])
    
    if valid_history.empty:
        st.warning("데이터가 없습니다. 아래 폼에서 첫 선수를 등록해주세요.")
        roster_summary = pd.DataFrame(columns=["PlayerName", "AgeGroup", "Age", "Gender", "MainPosition"])
    else:
        # 선수별 가장 최근 기록을 기준으로 기본 정보 요약
        roster_summary = valid_history.sort_values('GameDate').groupby('PlayerName').last()[['AgeGroup', 'Age', 'Gender', 'MainPosition']].reset_index()

    col_form, col_table = st.columns([1, 2])

    with col_form:
        st.markdown('<div class="fm-card"><div class="fm-card-title">➕ 신규 선수 등록</div>', unsafe_allow_html=True)
        with st.form("new_player_form"):
            n_name = st.text_input("선수 이름 (필수)", key="new_player_name")
            n_age = st.number_input("나이 (세)", 7, 16, 12)
            n_gender = st.selectbox("성별", ["남", "여"])
            n_main_pos = st.selectbox("주 포지션", VALID_POSITIONS)
            
            # 나이에 따른 연령대 그룹 자동 설정
            if n_age <= 11: n_age_group = "9-11세"
            elif n_age <= 13: n_age_group = "12-13세"
            else: n_age_group = "14-15세"

            add_player_submitted = st.form_submit_button("선수 로스터 등록")
            
            if add_player_submitted:
                if not n_name or n_name in roster_summary["PlayerName"].values:
                    st.error("이름을 입력하지 않았거나 이미 등록된 선수입니다.")
                else:
                    # 선수 등록은 데이터베이스에 기본 정보만 가진 초기 기록 행을 추가하는 방식으로 구현
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    
                    new_player_row = {
                        "PlayerName": n_name, "GameDate": today_str, 
                        "AgeGroup": n_age_group, "Age": n_age, "Gender": n_gender,
                        "MainPosition": n_main_pos, "Role": "타자", "PlayedPosition": n_main_pos, # 초기 역할 및 출전포지션 설정
                        "PA": 0, "AB": 0, "H": 0, "BB": 0, "K": 0, "TB": 0, "Errors": 0,
                        "HighZone_Whiffs": 0, "MidZone_Whiffs": 0, "LowZone_Whiffs": 0, "Chase_Zone10": 0,
                        "PitchesThrown": 0, "Strikes": 0, "IP_Outs": 0, "ER": 0, "WildPitches": 0, 
                        "PassedBalls": 0, "WildPitchesBlocked": 0, "StealAttempts": 0, 
                        "CaughtStealing": 0, "ThrowingErrors": 0,
                    }
                    st.session_state['df_history'] = pd.concat([st.session_state['df_history'], pd.DataFrame([new_player_row])], ignore_index=True)
                    save_data()
                    st.success(f"{n_name} 선수가 로스터에 등록되었습니다!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_table:
        st.markdown('<div class="fm-card"><div class="fm-card-title">📋 현재 선수단 로스터 (기본 정보 수정가능)</div>', unsafe_allow_html=True)
        
        # st.data_editor를 사용하여 선수 정보 요약 표 편집
        edited_roster_df = st.data_editor(
            roster_summary,
            key="roster_editor",
            use_container_width=True,
            column_config={
                "PlayerName": st.column_config.TextColumn("선수 이름", disabled=True), # 이름 수정불가 (경기 기록과 연동되므로)
                "AgeGroup": st.column_config.SelectboxColumn("연령대 그룹", options=["9-11세", "12-13세", "14-15세"]),
                "Age": st.column_config.NumberColumn("나이", min_value=7, max_value=16, step=1),
                "Gender": st.column_config.SelectboxColumn("성별", options=["남", "여"]),
                "MainPosition": st.column_config.SelectboxColumn("주 포지션", options=VALID_POSITIONS),
            }
        )

        # 저장 버튼
        if st.button("👥 로스터 기본 정보 변경 사항 저장", type="primary"):
            # 요약 표의 편집 내용을 전체 데이터베이스(`st.session_state['df_history']`)에 반영해야 함
            
            with st.spinner("로스터 정보를 데이터베이스에 반영 중..."):
                # 전체 데이터베이스 복사본
                updated_history = st.session_state['df_history'].copy()
                
                # 요약 표의 각 행을 돌면서 변경된 선수 정보를 업데이트
                for index, row in edited_roster_df.iterrows():
                    p_name = row['PlayerName']
                    # 해당 선수의 모든 기록 행을 찾아서 기본 정보 업데이트
                    updated_history.loc[updated_history['PlayerName'] == p_name, 'AgeGroup'] = row['AgeGroup']
                    updated_history.loc[updated_history['PlayerName'] == p_name, 'Age'] = row['Age']
                    updated_history.loc[updated_history['PlayerName'] == p_name, 'Gender'] = row['Gender']
                    updated_history.loc[updated_history['PlayerName'] == p_name, 'MainPosition'] = row['MainPosition']
                
                # 혹시 모를 None 값 제외 (스크린샷 문제 해결)
                cleaned_history = updated_history.dropna(subset=['PlayerName'])
                st.session_state['df_history'] = cleaned_history
                save_data()
                st.success("로스터 정보가 전체 데이터베이스에 반영되었습니다!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
