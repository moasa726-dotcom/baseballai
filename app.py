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

DB_FILE = "team_player_history_kr_v2.csv"

# --- 데이터 로드 및 초기화 ---
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # 날짜 컬럼 형식 통일
        df['GameDate'] = pd.to_datetime(df['GameDate']).dt.strftime('%Y-%m-%d')
        return df
    else:
        # 새로운 데이터 구조: 'MainPosition'(주 포지션) 컬럼 추가
        starter_df = pd.DataFrame({
            "PlayerName": ["김용준", "김용준", "박민수", "박민수", "이도윤", "이도윤", "최주원", "허이레"],
            "GameDate": ["2026-05-01", "2026-05-08", "2026-05-01", "2026-05-08", "2026-05-01", "2026-05-08", "2026-05-08", "2026-05-08"],
            "AgeGroup": ["14-15세", "14-15세", "12-13세", "12-13세", "9-11세", "9-11세", "14-15세", "12-13세"],
            "MainPosition": ["1B", "1B", "SS", "SS", "P", "P", "CF", "C"], # 주 포지션 데이터
            "Role": ["타자", "타자", "타자", "타자", "투수", "투수", "타자", "포수"],
            "PlayedPosition": ["1B", "1B", "SS", "2B", "P", "P", "CF", "C"], # 실제 출전 포지션
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

# 세션 상태에 데이터 저장 (수정 기능 갱신용)
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

VALID_POSITIONS = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]

# ==========================================
# 사이드바: 데이터 입력 및 관리
# ==========================================
st.sidebar.header("⚽ 데이터 관리 및 입력")

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

# 2. 직접 수동 입력
with st.sidebar.expander("➕ 수동 데이터 추가", expanded=False):
    with st.form("manual_entry_form"):
        m_player = st.text_input("선수 이름")
        m_date = st.date_input("경기 날짜", datetime.now())
        m_age = st.selectbox("연령대", ["9-11세", "12-13세", "14-15세"])
        
        col_main_pos, col_played_pos = st.columns(2)
        with col_main_pos:
            m_main_pos = st.selectbox("선수 주 포지션", VALID_POSITIONS)
        with col_played_pos:
            # 주 포지션과 다르게 출전했을 수 있으므로 별도 기록
            m_played_pos = st.selectbox("금개 실제 출전 포지션", VALID_POSITIONS)

        m_role = st.selectbox("역할", ["타자", "투수", "포수"])

        st.markdown("**기본 기록**")
        col_pa, col_ab, col_h = st.columns(3)
        m_pa = col_pa.number_input("타석", 0, 20, 0)
        m_ab = col_ab.number_input("타수", 0, 20, 0)
        m_h = col_h.number_input("안타", 0, 20, 0)
        
        col_bb, col_k, col_tb = st.columns(3)
        m_bb = col_bb.number_input("볼넷", 0, 20, 0)
        m_k = col_k.number_input("삼진", 0, 20, 0)
        m_tb = col_tb.number_input("루타수", 0, 30, 0)
        
        m_err = st.number_input("실책 (야수/투수)", 0, 10, 0)

        # 역할별 상세 기록 입력은 복잡성을 줄이기 위해 생략 (필요시 추가 가능)

        submitted = st.form_submit_button("기록 저장")
        if submitted and m_player:
            new_row = {
                "PlayerName": m_player, "GameDate": m_date.strftime('%Y-%m-%d'), "AgeGroup": m_age,
                "MainPosition": m_main_pos, "Role": m_role, "PlayedPosition": m_played_pos,
                "PA": m_pa, "AB": m_ab, "H": m_h, "BB": m_bb, "K": m_k, "TB": m_tb, "Errors": m_err,
                "HighZone_Whiffs": 0, "MidZone_Whiffs": 0, "LowZone_Whiffs": 0, "Chase_Zone10": 0,
                "PitchesThrown": 0, "Strikes": 0, "IP_Outs": 0, "ER": 0, "WildPitches": 0, 
                "PassedBalls": 0, "WildPitchesBlocked": 0, "StealAttempts": 0, 
                "CaughtStealing": 0, "ThrowingErrors": 0,
            }
            st.session_state['df_history'] = pd.concat([st.session_state['df_history'], pd.DataFrame([new_row])], ignore_index=True)
            save_data()
            st.sidebar.success(f"{m_player} 선수의 기록이 추가되었습니다!")
            st.rerun()

st.sidebar.download_button(
    label="전체 데이터 CSV 다운로드",
    data=df_history.to_csv(index=False),
    file_name="team_player_history_kr_all.csv",
    mime="text/csv",
)

# ==========================================
# 메인 화면: 탭 구성
# ==========================================
tabs = st.tabs(["📊 선수단 종합", "🛡️ 수비/포지션", "👤 개인 프로필", "🛠️ 경기 기록 수정/삭제", "📋 AI 선발 라인업 추천"])

# [탭 1, 2, 3은 기존 코드 유지 (생략 - 실제 파일에는 포함됨)]
with tabs[0]: st.write("선수단 종합 비교 화면 (기존 코드)")
with tabs[1]: st.write("수비/포지션 분석 화면 (기존 코드)")
with tabs[2]: st.write("개인 프로필 화면 (기존 코드)")

# ==========================================
# 탭 4: 경기 기록 수정 및 삭제 (요청 기능)
# ==========================================
with tabs[3]:
    st.markdown("### 🛠️ 이전에 올렸던 경기 기록 수정 및 삭제")
    st.markdown("아래 표에서 직접 데이터를 수정하거나, 왼쪽 체크박스를 선택하여 행을 삭제할 수 있습니다. 변경 후 반드시 **'변경 사항 저장'** 버튼을 눌러주세요.")

    # st.data_editor를 사용하여 데이터 편집 인터페이스 제공
    # num_rows="dynamic"으로 행 삭제 기능 활성화
    edited_df = st.data_editor(
        st.session_state['df_history'],
        key="history_editor",
        num_rows="dynamic", # 행 추가/삭제 가능
        use_container_width=True,
        # 주요 컬럼들 드롭다운 설정
        column_config={
            "AgeGroup": st.column_config.SelectboxColumn("연령대", options=["9-11세", "12-13세", "14-15세"]),
            "MainPosition": st.column_config.SelectboxColumn("주 포지션", options=VALID_POSITIONS),
            "PlayedPosition": st.column_config.SelectboxColumn("출전 포지션", options=VALID_POSITIONS),
            "Role": st.column_config.SelectboxColumn("역할", options=["타자", "투수", "포수"]),
            "GameDate": st.column_config.DateColumn("경기 날짜", format="YYYY-MM-DD")
        }
    )

    col_save, col_reset = st.columns([1, 5])
    
    if col_save.button("📝 변경 사항 저장", type="primary"):
        st.session_state['df_history'] = edited_df
        save_data()
        st.success("데이터베이스가 성공적으로 업데이트되었습니다!")
        st.rerun()
        
    if col_reset.button("🔄 되돌리기"):
        st.rerun() # 저장하지 않고 세션 상태 초기화

# ==========================================
# 탭 5: AI 선발 라인업 추천 (레퍼런스 이미지 적용)
# ==========================================
with tabs[4]:
    st.markdown("### 📋 통계 기반 경기 당일 포지션별 선발 추천 및 라인업")
    
    if df_history.empty:
        st.warning("데이터베이스가 비어 있습니다. 데이터를 먼저 입력해주세요.")
        st.stop()

    # 1. 선수별 요약 통계 계산 (추천 로직용)
    # 선수별 가장 최근 연령대와 주 포지션 가져오기
    player_base = df_history.sort_values('GameDate').groupby('PlayerName').last()[['AgeGroup', 'MainPosition']]
    
    # 통계 합계 계산
    agg_stats = df_history.groupby('PlayerName').agg({
        'PA': 'sum', 'AB': 'sum', 'H': 'sum', 'TB': 'sum', 'Errors': 'sum'
    })
    
    # 지표 계산
    agg_stats['타율'] = (agg_stats['H'] / agg_stats['AB']).fillna(0)
    agg_stats['장타율'] = (agg_stats['TB'] / agg_stats['AB']).fillna(0)
    
    # 기본 데이터 병합
    recommend_df = player_base.merge(agg_stats, left_index=True, right_index=True)

    # 2. 포지션별 추천 로직 (심플 알고리즘)
    # P (투수): 제구력/스태미나 기준 (여기선 데이터 부족으로 랜덤 또는 최근 투수 역할 수행자)
    # C (포수): 블로킹/도루저지 기준
    # 1B, 3B (코너 내야): 장타율 최상위권
    # SS, 2B (키스톤 내야), CF (중견수): 실책 적고 타율 준수한 선수
    # LF, RF (코너 외야): 주 포지션이 외야인 선수 중 타격 좋은 선수

    final_lineup = {}
    used_players = set()

    # 추천 우선 순위 및 로직 정의
    position_logic = [
        ("P", lambda df: df[df['MainPosition'] == 'P']), # 투수는 주포지션 최우선
        ("C", lambda df: df[df['MainPosition'] == 'C']), # 포수는 주포지션 최우선
        ("CF", lambda df: df[df['MainPosition'] == 'CF']), # 중견수 주포지션
        ("SS", lambda df: df[df['MainPosition'] == 'SS']), # 유격수 주포지션
        ("1B", lambda df: df.sort_values('장타율', ascending=False)), # 1루수는 장타력
        ("3B", lambda df: df.sort_values('장타율', ascending=False)), # 3루수도 장타력
        ("2B", lambda df: df.sort_values('Errors', ascending=True)), # 2루수는 실책 적은 순
        ("RF", lambda df: df[df['MainPosition'].isin(['RF', 'OF'])]), # 우익수
        ("LF", lambda df: df[df['MainPosition'].isin(['LF', 'OF'])])  # 좌익수
    ]

    for pos, logic_func in position_logic:
        # 아직 배정되지 않은 선수 데이터셋
        available_df = recommend_df[~recommend_df.index.isin(used_players)]
        
        # 로직 적용
        candidates = logic_func(available_df)
        
        if not candidates.empty:
            # 타율 순으로 정렬하여 가장 높은 선수 선발
            top_player = candidates.sort_values('타율', ascending=False).index[0]
            final_lineup[pos] = top_player
            used_players.add(top_player)
        else:
            # 후보가 없으면 남은 선수 중 타율 높은 순으로 임의 배정
            if not available_df.empty:
                fallback_player = available_df.sort_values('타율', ascending=False).index[0]
                final_lineup[pos] = fallback_player
                used_players.add(fallback_player)
            else:
                final_lineup[pos] = "미정"

    # 타순 결정 (심플: 타율 순 1~9번)
    lineup_players_df = recommend_df[recommend_df.index.isin(final_lineup.values())]
    batting_order = lineup_players_df.sort_values('타율', ascending=False).index.tolist()
    
    # 역으로 포지션 매핑
    player_to_pos = {v: k for k, v in final_lineup.items()}

    col_visual, col_list = st.columns([1.5, 1])

    with col_visual:
        st.markdown('<div class="fm-card"><div class="fm-card-title">🏟️ 그래픽 선발 라인업 (레퍼런스 참고)</div>', unsafe_allow_html=True)
        
        # Plotly를 이용한 야구장 그래픽 및 포지션 마커 생성
        # 레퍼런스 이미지의 어두운 톤과 빨간색 라인 적용
        
        fig_field = go.Figure()

        # 1. 야구장 외곽선 및 빨간색 아크(수비 라인) 그리기
        # 내야 다이아몬드
        fig_field.add_trace(go.Scatter(
            x=[0, 1, 0, -1, 0], y=[0, 1, 2, 1, 0],
            mode='lines', line=dict(color='#A0AEC0', width=2), showlegend=False
        ))
        # 파울 라인
        fig_field.add_trace(go.Scatter(
            x=[0, 2.5], y=[0, 2.5], mode='lines', line=dict(color='#A0AEC0', width=1), showlegend=False
        ))
        fig_field.add_trace(go.Scatter(
            x=[0, -2.5], y=[0, 2.5], mode='lines', line=dict(color='#A0AEC0', width=1), showlegend=False
        ))
        # 외야 빨간색 아크
        theta = np.linspace(np.pi/4, 3*np.pi/4, 50)
        r = 3.2
        fig_field.add_trace(go.Scatter(
            x=r*np.cos(theta), y=r*np.sin(theta)-1,
            mode='lines', line=dict(color='#EF4444', width=3), showlegend=False
        ))

        # 2. 포지션별 마커 좌표 정의 (레퍼런스 이미지 기반 조정)
        pos_coords = {
            "P": (0, 0.8), "C": (0, -0.2),
            "1B": (1.1, 1.1), "2B": (0.5, 1.8), "SS": (-0.5, 1.8), "3B": (-1.1, 1.1),
            "LF": (-1.8, 2.6), "CF": (0, 3.0), "RF": (1.8, 2.6)
        }

        # 3. 마커 및 선수 이름 추가
        for pos in VALID_POSITIONS:
            x, y = pos_coords[pos]
            player_name = final_lineup.get(pos, "미정")
            
            # 포지션 원형 마커 (점선 스타일)
            fig_field.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                marker=dict(size=40, color='#14181E', line=dict(color='#4A5568', width=2, dash='dash')),
                text=f"<b>{pos}</b><br>{player_name}",
                textposition="middle center",
                textfont=dict(color="#E2E8F0", size=10),
                showlegend=False
            ))

        fig_field.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 3]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
            paper_bgcolor="#121417", plot_bgcolor="#121417",
            margin=dict(l=10, r=10, t=10, b=10),
            height=500
        )
        
        st.plotly_chart(fig_field, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_list:
        st.markdown('<div class="fm-card"><div class="fm-card-title">타순 • 수비 위치 목록</div>', unsafe_allow_html=True)
        
        # 레퍼런스 이미지 스타일의 타순 목록 표시
        for i, player in enumerate(batting_order):
            pos = player_to_pos.get(player, "??")
            
            # 각 타순을 시각적으로 구분하는 HTML
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; background: #0F1115; border: 1px solid #334155; border-radius: 4px; padding: 8px; margin-bottom: 6px;">
                    <span style="color: #EF4444; font-weight: bold; font-size: 1.1rem; margin-right: 15px; width: 20px; text-align: center;">{i+1}</span>
                    <span style="color: #F8FAFC; font-weight: 500; flex-grow: 1;">{player}</span>
                    <span style="background: #2D3748; color: #38BDF8; padding: 2px 10px; border-radius: 4px; font-weight: bold; font-size: 0.9rem;">{pos}</span>
                </div>
                """, unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # 벤치 선수 목록 (라인업에 포함 안 된 선수)
        st.markdown('<div class="fm-card"><div class="fm-card-title">벤치 멤버</div>', unsafe_allow_html=True)
        bench_players = unique_players_list = sorted(df_history["PlayerName"].unique())
        bench_players = [p for p in bench_players if p not in used_players]
        
        if bench_players:
            bench_html = ""
            for p in bench_players:
                bench_html += f'<span class="bench-player">{p}</span>'
            st.markdown(bench_html, unsafe_allow_html=True)
        else:
            st.caption("벤치 멤버가 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("FM Youth Baseball Director Hub v2.0 | AI 추천 시스템 탑재")
