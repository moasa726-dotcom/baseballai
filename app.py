import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="FM 유소년 야구단 디렉터 허브",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    </style>
""",
    unsafe_allow_html=True,
)

DB_FILE = "team_player_history_kr.csv"

def load_or_init_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        starter_df = pd.DataFrame({
            "PlayerName": ["김용준", "김용준", "박민수", "박민수", "이도윤", "이도윤"],
            "GameDate": ["2026-05-01", "2026-05-08", "2026-05-01", "2026-05-08", "2026-05-01", "2026-05-08"],
            "AgeGroup": ["14-15세 그룹", "14-15세 그룹", "12-13세 그룹", "12-13세 그룹", "9-11세 그룹", "9-11세 그룹"],
            "Role": ["타자", "타자", "타자", "타자", "투수", "투수"],
            "Position": ["1루수(1B)", "1루수(1B)", "유격수(SS)", "유격수(SS)", "선발투수(SP)", "선발투수(SP)"],
            "PA": [4, 3, 4, 4, 0, 0],
            "AB": [3, 3, 3, 4, 0, 0],
            "H": [1, 2, 0, 1, 0, 0],
            "BB": [1, 0, 1, 0, 1, 1],
            "K": [1, 0, 2, 1, 3, 2],
            "TB": [1, 3, 0, 1, 0, 0],
            "Errors": [0, 0, 1, 0, 0, 0],
            "HighZone_Whiffs": [2, 0, 4, 2, 0, 0],
            "MidZone_Whiffs": [0, 1, 1, 1, 0, 0],
            "LowZone_Whiffs": [1, 0, 3, 2, 0, 0],
            "Chase_Zone10": [1, 0, 3, 2, 0, 0],
            "PitchesThrown": [0, 0, 0, 0, 45, 50],
            "Strikes": [0, 0, 0, 0, 29, 33],
            "IP_Outs": [0, 0, 0, 0, 6, 6],
            "ER": [0, 0, 0, 0, 1, 2],
            "WildPitches": [0, 0, 0, 0, 0, 1],
            "PassedBalls": [0, 0, 0, 0, 0, 0],
            "WildPitchesBlocked": [0, 0, 0, 0, 0, 0],
            "StealAttempts": [0, 0, 0, 0, 0, 0],
            "CaughtStealing": [0, 0, 0, 0, 0, 0],
            "ThrowingErrors": [0, 0, 0, 0, 0, 0],
        })
        starter_df.to_csv(DB_FILE, index=False)
        return starter_df

df_history = load_or_init_db()

def fm_color_class(val):
    if val >= 15: return "val-elite"
    elif val >= 11: return "val-good"
    elif val >= 7: return "val-avg"
    else: return "val-poor"

# --- SIDEBAR: 데이터 수집 및 직접 입력 ---
st.sidebar.header("⚽ 데이터 수집 및 입력")
uploaded_file = st.sidebar.file_uploader("새 경기 CSV 업로드", type=["csv"])

if uploaded_file is not None:
    try:
        new_data = pd.read_csv(uploaded_file)
        df_history = pd.concat([df_history, new_data], ignore_index=True)
        df_history.to_csv(DB_FILE, index=False)
        st.sidebar.success("새 경기 스탯이 데이터베이스에 병합되었습니다!")
    except Exception as e:
        st.sidebar.error(f"CSV 로드 오류: {e}")

with st.sidebar.expander("➕ 직접 수동 데이터 입력", expanded=False):
    with st.form("manual_entry_form"):
        unique_players_list = sorted(df_history["PlayerName"].unique()) if not df_history.empty else []
        m_player = st.text_input("선수 이름 (기존 선수 또는 새 이름)")
        m_date = st.date_input("경기 날짜")
        m_age = st.selectbox("연령대", ["9-11세 그룹", "12-13세 그룹", "14-15세 그룹"])
        
        col_role, col_pos = st.columns(2)
        with col_role:
            m_role = st.selectbox("역할", ["타자", "투수", "포수"])
        with col_pos:
            m_pos = st.selectbox("포지션", ["내야수(INF)", "외야수(OF)", "투수(P)", "포수(C)"])

        st.markdown("**타자 기록 (투수/포수일 경우 0 유지)**")
        col_a, col_b = st.columns(2)
        with col_a:
            m_pa = st.number_input("타석 (PA)", 0, 20, 0)
            m_ab = st.number_input("타수 (AB)", 0, 20, 0)
            m_h = st.number_input("안타 (H)", 0, 20, 0)
            m_bb = st.number_input("볼넷 (BB)", 0, 20, 0)
        with col_b:
            m_k = st.number_input("삼진 (K)", 0, 20, 0)
            m_tb = st.number_input("루타수 (TB)", 0, 30, 0)
            m_err = st.number_input("일반 실책", 0, 10, 0)

        st.markdown("**투수/포수 전용 기록**")
        col_c, col_d = st.columns(2)
        with col_c:
            m_ip_outs = st.number_input("잡은 아웃카운트", 0, 30, 0)
            m_pitches = st.number_input("투구수", 0, 120, 0)
            m_strikes = st.number_input("스트라이크 수", 0, 100, 0)
            m_er = st.number_input("자책점 (ER)", 0, 20, 0)
        with col_d:
            m_wp = st.number_input("폭투", 0, 10, 0)
            m_pb = st.number_input("포일(Passed Ball)", 0, 10, 0)
            m_cs = st.number_input("도루 저지", 0, 10, 0)
            m_att = st.number_input("도루 허용", 0, 10, 0)

        st.markdown("**헛스윙 / 존 프로필 (타자)**")
        m_h_whiff = st.number_input("높은 존 헛스윙", 0, 20, 0)
        m_mid_whiff = st.number_input("중간 존 헛스윙", 0, 20, 0)
        m_low_whiff = st.number_input("낮은 존 헛스윙", 0, 20, 0)
        m_chase10 = st.number_input("유인구(존 이탈) 스윙", 0, 20, 0)

        submitted = st.form_submit_button("경기 기록 저장")
        if submitted and m_player:
            new_row = {
                "PlayerName": m_player, "GameDate": str(m_date), "AgeGroup": m_age,
                "Role": m_role, "Position": m_pos, "PA": m_pa, "AB": m_ab, "H": m_h, 
                "BB": m_bb, "K": m_k, "TB": m_tb, "Errors": m_err,
                "HighZone_Whiffs": m_h_whiff, "MidZone_Whiffs": m_mid_whiff, 
                "LowZone_Whiffs": m_low_whiff, "Chase_Zone10": m_chase10,
                "PitchesThrown": m_pitches, "Strikes": m_strikes, "IP_Outs": m_ip_outs, 
                "ER": m_er, "WildPitches": m_wp, "PassedBalls": m_pb,
                "WildPitchesBlocked": 0, "StealAttempts": m_att, 
                "CaughtStealing": m_cs, "ThrowingErrors": 0,
            }
            df_history = pd.concat([df_history, pd.DataFrame([new_row])], ignore_index=True)
            df_history.to_csv(DB_FILE, index=False)
            st.sidebar.success(f"{m_player} 선수의 기록이 추가되었습니다!")
            st.rerun()

st.sidebar.download_button(
    label="전체 선수단 CSV 다운로드",
    data=df_history.to_csv(index=False),
    file_name="team_player_history_kr.csv",
    mime="text/csv",
)

# --- 탭 구성 ---
tab_squad, tab_defense, tab_profile = st.tabs(["📊 선수단 종합 비교", "🛡️ 수비/포지션 분석", "👤 개인 프로필 (FM 스타일)"])

# ==========================================
# 탭 1: 선수단 종합 비교
# ==========================================
with tab_squad:
    st.markdown("### 📈 전체 선수단 공격 및 투구 지표")
    
    # 타자 요약 데이터 프레임 생성
    hitters = df_history[df_history['Role'] == '타자'].copy()
    if not hitters.empty:
        h_agg = hitters.groupby(['PlayerName', 'AgeGroup', 'Position']).agg({
            'PA': 'sum', 'AB': 'sum', 'H': 'sum', 'BB': 'sum', 'K': 'sum', 'TB': 'sum'
        }).reset_index()
        h_agg['타율(AVG)'] = (h_agg['H'] / h_agg['AB']).fillna(0).round(3)
        h_agg['출루율(OBP)'] = ((h_agg['H'] + h_agg['BB']) / (h_agg['AB'] + h_agg['BB'])).fillna(0).round(3)
        h_agg['장타율(SLG)'] = (h_agg['TB'] / h_agg['AB']).fillna(0).round(3)
        h_agg['OPS'] = (h_agg['출루율(OBP)'] + h_agg['장타율(SLG)']).round(3)
        
        st.markdown("**타자 기록 요약**")
        st.dataframe(h_agg[['PlayerName', 'AgeGroup', 'Position', 'PA', 'H', '타율(AVG)', 'OPS']], use_container_width=True)
    
    # 투수 요약 데이터 프레임 생성
    pitchers = df_history[df_history['Role'] == '투수'].copy()
    if not pitchers.empty:
        p_agg = pitchers.groupby(['PlayerName', 'AgeGroup', 'Position']).agg({
            'IP_Outs': 'sum', 'PitchesThrown': 'sum', 'Strikes': 'sum', 'K': 'sum', 'BB': 'sum', 'ER': 'sum'
        }).reset_index()
        p_agg['이닝(IP)'] = (p_agg['IP_Outs'] // 3).astype(str) + "." + (p_agg['IP_Outs'] % 3).astype(str)
        p_agg['스트라이크%'] = ((p_agg['Strikes'] / p_agg['PitchesThrown']) * 100).fillna(0).round(1)
        p_agg['평균자책점(ERA)'] = ((p_agg['ER'] * 9) / (p_agg['IP_Outs'] / 3)).fillna(0).round(2)
        
        st.markdown("**투수 기록 요약**")
        st.dataframe(p_agg[['PlayerName', 'AgeGroup', '이닝(IP)', '평균자책점(ERA)', 'K', 'BB', '스트라이크%']], use_container_width=True)

# ==========================================
# 탭 2: 수비/포지션 분석
# ==========================================
with tab_defense:
    st.markdown("### 🛡️ 수비 및 포지션 안정성 현황")
    
    def_agg = df_history.groupby(['PlayerName', 'Position', 'Role']).agg({
        'Errors': 'sum', 'ThrowingErrors': 'sum', 'PassedBalls': 'sum', 
        'WildPitchesBlocked': 'sum', 'StealAttempts': 'sum', 'CaughtStealing': 'sum'
    }).reset_index()
    
    def_agg['총 실책'] = def_agg['Errors'] + def_agg['ThrowingErrors']
    def_agg['도루저지율(%)'] = ((def_agg['CaughtStealing'] / def_agg['StealAttempts']) * 100).fillna(0).round(1)
    
    st.markdown("**야수 실책 및 포수 지표**")
    st.dataframe(
        def_agg[['PlayerName', 'Position', '총 실책', 'Errors', 'ThrowingErrors', 'PassedBalls', '도루저지율(%)']], 
        use_container_width=True
    )
    
    # 간단한 시각화 (포지션별 실책 수)
    if not def_agg.empty and def_agg['총 실책'].sum() > 0:
        fig_err = px.bar(def_agg, x='PlayerName', y='총 실책', color='Position', title="선수별 총 수비 실책")
        fig_err.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1"))
        st.plotly_chart(fig_err, use_container_width=True)

# ==========================================
# 탭 3: 개인 프로필 (FM 스타일)
# ==========================================
with tab_profile:
    unique_players = sorted(df_history["PlayerName"].unique())
    selected_player = st.selectbox("🔍 프로필 조회할 선수 선택:", unique_players)

    player_df = df_history[df_history["PlayerName"] == selected_player].sort_values(by="GameDate")
    latest_tier = player_df["AgeGroup"].iloc[-1] if "AgeGroup" in player_df.columns else "미정"
    player_role = player_df["Role"].iloc[-1] if "Role" in player_df.columns else "타자"
    player_pos = player_df["Position"].iloc[-1] if "Position" in player_df.columns else "내야수"

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

    # --- 상단 헤더 배너 ---
    with st.container():
        top_col1, top_col2 = st.columns([3, 1])

        with top_col1:
            st.caption(f"로스터 프로필 • {latest_tier} • 포지션: {player_pos} ({player_role})")
            st.title(selected_player)

            if player_role == "타자":
                st.markdown(f"**OPS:** `{ops:.3f}` &nbsp;|&nbsp; **타율:** `{avg:.3f}` &nbsp;|&nbsp; **삼진율(K%):** `{k_rate*100:.1f}%`")
            elif player_role == "투수":
                st.markdown(f"**이닝:** `{ip_display}` &nbsp;|&nbsp; **스트라이크 %:** `{strike_pct:.1f}%` &nbsp;|&nbsp; **탈삼진:** `{pitcher_k}` &nbsp;|&nbsp; **볼넷:** `{pitcher_bb}`")
            else:
                st.markdown(f"**블로킹 성공:** `{blocked_balls}` &nbsp;|&nbsp; **포일:** `{passed_balls}` &nbsp;|&nbsp; **도루저지:** `{cs_caught}/{cs_attempts}`")

        with top_col2:
            st.markdown(
                """
                <div style="background: #0F1115; padding: 12px; border-radius: 6px; border: 1px solid #334155; text-align: center;">
                    <div style="font-size: 0.75rem; color: #94A3B8;">팀 내 역할</div>
                    <div style="font-size: 1.1rem; color: #4ADE80; font-weight: 700;">핵심 유망주</div>
                </div>
                """, unsafe_allow_html=True
            )

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
                    <span class="attr-val {c_class}">{val}</span>
                </div>
                """, unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_report:
        st.markdown('<div class="fm-card"><div class="fm-card-title">📋 코치 리포트 (장/단점)</div>', unsafe_allow_html=True)

        pros, cons = [], []
        if player_role == "타자":
            if attr_contact >= 13: pros.append("안정적인 배트 컨트롤; 스윙 궤적이 좋습니다.")
            else: cons.append("타이밍이 불안정하고 헛스윙 비율이 높습니다.")
            if attr_discipline >= 12: pros.append("차분한 타석 접근; 좋은 스윙 결정을 내립니다.")
            else: cons.append("스트라이크 존을 벗어나는 공에 자주 방망이가 나갑니다.")
            if attr_defense >= 15: pros.append("부드러운 글러브 질과 안정적인 송구 능력을 보유함.")
            else: cons.append("압박 상황에서 평범한 실책을 범하는 경향이 있음.")
        elif player_role == "투수":
            if strike_pct >= 60: pros.append("초구 스트라이크 비율이 높고 공격적입니다.")
            else: cons.append("카운트가 불리해지며 패스트볼 제구에 어려움을 겪음.")
            if pitcher_bb <= 2: pros.append("도망가지 않는 피칭으로 볼넷 허용이 적습니다.")
            else: cons.append("이닝당 볼넷 허용 빈도가 너무 높음.")
        else:
            if blocked_balls >= passed_balls: pros.append("원바운드 변화구를 두려워하지 않고 잘 막아냅니다.")
            else: cons.append("낮은 공을 뒤로 빠뜨리는 실수가 종종 나옴.")
            if cs_caught > 0: pros.append("팝타임이 준수하여 주자의 도루를 효과적으로 억제함.")
            else: cons.append("도루 상황 시 글러브에서 공을 빼는 동작(트랜스퍼)이 느림.")

        if not pros: pros.append("팀 훈련에 성실하게 임하며 기본기를 다지는 중.")
        if not cons: cons.append("현재 데이터 상 뚜렷한 약점이 기록되지 않았습니다.")

        st.markdown("**🟢 장점 (PROS)**")
        for p in pros: st.markdown(f"<span class='pro-tag'>+</span> {p}", unsafe_allow_html=True)

        st.markdown("<br>**🔴 단점 (CONS)**", unsafe_allow_html=True)
        for c in cons: st.markdown(f"<span class='con-tag'>-</span> {c}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_zone:
        st.markdown('<div class="fm-card"><div class="fm-card-title">🎯 존 분석 및 안전 모니터링</div>', unsafe_allow_html=True)
        if player_role == "타자":
            high_whiffs = player_df["HighZone_Whiffs"].sum()
            mid_whiffs = player_df["MidZone_Whiffs"].sum()
            low_whiffs = player_df["LowZone_Whiffs"].sum()
            chase_count = player_df["Chase_Zone10"].sum()

            zone_matrix = np.array([
                [high_whiffs * 0.4, high_whiffs * 0.2, high_whiffs * 0.4],
                [mid_whiffs * 0.3, mid_whiffs * 0.4, mid_whiffs * 0.3],
                [low_whiffs * 0.4, low_whiffs * 0.2, low_whiffs * 0.4],
            ])

            fig_zone = px.imshow(
                zone_matrix,
                x=["바깥쪽", "가운데", "몸쪽"],
                y=["상단 (1-3)", "중단 (4-6)", "하단 (7-9)"],
                color_continuous_scale="Reds",
                text_auto=True,
            )
            fig_zone.update_traces(textfont_size=20)
            fig_zone.update_layout(
                height=210, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1")
            )
            st.plotly_chart(fig_zone, use_container_width=True)
            st.caption(f"스트라이크 존을 완전히 벗어난 유인구 스윙 횟수: **{chase_count}**")
        else:
            st.metric("총 투구 이닝 (워크로드)", f"{ip_display} 이닝")
            st.metric("스트라이크 비율", f"{strike_pct:.1f}% 스트라이크")
            st.caption("💪 어깨 및 팔꿈치 보호 모니터링: 경기별 투구수 제한 가이드라인 준수 필수.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="fm-card"><div class="fm-card-title">🛠️ 주간 훈련 추천 (코치진 포커스)</div>', unsafe_allow_html=True)
    tips = []
    if player_role == "타자":
        tips.append("<b>선구안 및 유인구 대처:</b> 존 밖으로 빠지는 공에 스윙하면 감점되는 10분 'Take-or-Drive' 배팅 훈련 진행.")
        tips.append("<b>컨택 훈련:</b> 하이-티(High-tee) 및 소프트 토스 훈련으로 센터 방면으로 레벨 스윙을 유지하는 데 집중.")
    elif player_role == "투수":
        tips.append("<b>초구 스트라이크 잡기:</b> 불펜 피칭 시 타자 카운트(1-0)로 넘어가기 전, 존 상하단에 패스트볼을 꽂아넣는 훈련.")
    else:
        tips.append("<b>블로킹 및 퀵 모션:</b> 코치가 땅볼로 던져주는 테니스공을 10분간 블로킹하고 즉시 2루로 풋워크 하는 훈련.")

    for t in tips: st.markdown(f"• {t}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="fm-card"><div class="fm-card-title">📤 맞춤형 데이터 내보내기</div>', unsafe_allow_html=True)
    export_audience = st.radio("내보낼 포맷 선택:", ["👨‍👩‍👦 학부모용 성장 리포트 (텍스트)", "📊 코치 분석용 통계 (CSV)"], horizontal=True)

    if "학부모용" in export_audience:
        pro_text = pros[0] if pros else "훈련에 매우 긍정적이고 열심히 참여하고 있습니다."
        tip_text = tips[0].replace("<b>", "").replace("</b>", "") if tips else "기본기 및 밸런스 유지에 집중하고 있습니다."

        parent_report = f"""==================================================
선수 성장 스냅샷: {selected_player}
소속 연령대: {latest_tier} ({player_pos})
==================================================

🌟 현재 잘하고 있는 점 (강점):
• {pro_text}

🎯 이번 주 팀 훈련 목표:
• {tip_text}

🏡 학부모님 홈 서포트 팁:
• 마당이나 공터에서 5~10분 정도 가볍게 캐치볼을 해주세요. 경기 결과보다는 과정과 땀방울을 칭찬해주세요!

---
코치 및 스태프 드림
"""
        st.markdown("##### 📄 학부모 리포트 미리보기:")
        st.text_area("Parent Report Text", value=parent_report, height=180, label_visibility="collapsed")
        st.download_button(label="📥 학부모용 리포트 다운로드 (.txt)", data=parent_report, file_name=f"{selected_player}_학부모_리포트.txt", mime="text/plain")
    else:
        analytics_export = player_df.copy()
        st.markdown("##### 📊 통계 데이터셋 미리보기:")
        st.dataframe(analytics_export, use_container_width=True)
        st.download_button(label="📥 통계 데이터 다운로드 (.csv)", data=analytics_export.to_csv(index=False), file_name=f"{selected_player}_통계_로그.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)
