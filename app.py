import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from data.demo_data import generate_demo_ports, generate_demo_vessels
from simulation.optimizer import SimpleOptimizer

# ページ設定
st.set_page_config(
    page_title="穀物配船最適化MVP",
    page_icon="🚢",
    layout="wide"
)

def main():
    st.title("🚢 穀物配船最適化システム (MVP)")
    st.markdown("---")
    
    # データ初期化
    if 'initialized' not in st.session_state:
        initialize_data()
    
    # メインタブ
    tab1, tab2, tab3 = st.tabs(["📊 ダッシュボード", "⚙️ 最適化実行", "📋 詳細データ"])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_optimization()
    
    with tab3:
        show_detail_data()

def initialize_data():
    """データ初期化"""
    st.session_state.berths = generate_demo_ports()
    st.session_state.vessels = generate_demo_vessels()
    st.session_state.initialized = True

@st.cache_data
def get_berth_data():
    """バースデータをDataFrame形式で取得"""
    berths = st.session_state.berths
    return pd.DataFrame([
        {
            "バース名": berth.name,
            "港湾": berth.port_name,
            "最大容量": f"{berth.max_capacity:,}t",
            "日次荷役能力": f"{berth.daily_handling_capacity:,}t/日",
            "日次使用料": f"¥{berth.daily_cost:,}"
        }
        for berth in berths
    ])

@st.cache_data
def get_vessel_data():
    """船舶データをDataFrame形式で取得"""
    vessels = st.session_state.vessels
    return pd.DataFrame([
        {
            "船名": vessel.name,
            "到着予定日": vessel.arrival_date.strftime("%Y-%m-%d"),
            "出発港": vessel.origin_port,
            "総貨物量": f"{vessel.total_quantity:,}t",
            "貨物構成": ", ".join([f"{cargo.cargo_type.value}:{cargo.quantity:,}t" for cargo in vessel.cargos])
        }
        for vessel in vessels
    ])

def show_dashboard():
    """ダッシュボード表示"""
    st.header("📊 システム概要")
    
    # KPI表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("対象船舶数", len(st.session_state.vessels))
    
    with col2:
        total_cargo = sum(vessel.total_quantity for vessel in st.session_state.vessels)
        st.metric("総貨物量", f"{total_cargo:,} t")
    
    with col3:
        st.metric("利用可能バース数", len(st.session_state.berths))
    
    with col4:
        ports = set(berth.port_name for berth in st.session_state.berths)
        st.metric("対象港湾数", len(ports))
    
    # 船舶到着スケジュール
    st.subheader("🚢 船舶到着予定")
    vessel_df = get_vessel_data()
    st.dataframe(vessel_df, use_container_width=True)
    
    # 到着日別貨物量グラフ
    fig = px.bar(
        vessel_df,
        x="到着予定日",
        y=[int(qty.replace(",", "").replace("t", "")) for qty in vessel_df["総貨物量"]],
        title="日別到着貨物量",
        labels={"y": "貨物量 (トン)", "x": "到着予定日"}
    )
    st.plotly_chart(fig, use_container_width=True)

def show_optimization():
    """最適化実行・結果表示"""
    st.header("⚙️ 配船最適化")
    
    st.info("現在のアルゴリズム: FCFS (First Come First Served - 先着順)")
    
    if st.button("🚀 最適化実行", type="primary", use_container_width=True):
        with st.spinner("最適化計算中..."):
            optimizer = SimpleOptimizer(st.session_state.berths, st.session_state.vessels)
            schedules = optimizer.optimize()
            st.session_state.optimization_result = schedules
        
        st.success(f"最適化完了！ {len(schedules)}隻の配船が決定されました。")
    
    # 結果表示
    if 'optimization_result' in st.session_state:
        schedules = st.session_state.optimization_result
        
        # サマリー
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_cost = sum(schedule.total_cost for schedule in schedules)
            st.metric("総コスト", f"¥{total_cost:,}")
        
        with col2:
            st.metric("配船成功", f"{len(schedules)}隻")
        
        with col3:
            unassigned = len(st.session_state.vessels) - len(schedules)
            st.metric("未配船", f"{unassigned}隻")
        
        # スケジュール表
        st.subheader("📅 配船スケジュール")
        
        if schedules:
            schedule_data = []
            for schedule in schedules:
                end_date = schedule.start_date + timedelta(days=schedule.handling_days)
                schedule_data.append({
                    "船名": schedule.vessel.name,
                    "バース": schedule.berth.name,
                    "港湾": schedule.berth.port_name,
                    "開始日": schedule.start_date.strftime("%Y-%m-%d"),
                    "終了日": end_date.strftime("%Y-%m-%d"),
                    "荷役日数": f"{schedule.handling_days}日",
                    "貨物量": f"{schedule.vessel.total_quantity:,}t",
                    "総コスト": f"¥{schedule.total_cost:,}"
                })
            
            df_schedule = pd.DataFrame(schedule_data)
            st.dataframe(df_schedule, use_container_width=True)
            
            # ガントチャート
            st.subheader("📊 スケジュールガントチャート")
            
            fig = go.Figure()
            
            colors = px.colors.qualitative.Set3
            for i, schedule in enumerate(schedules):
                start = schedule.start_date
                end = start + timedelta(days=schedule.handling_days)
                
                fig.add_trace(go.Scatter(
                    x=[start, end],
                    y=[schedule.berth.name, schedule.berth.name],
                    mode='lines',
                    line=dict(width=15, color=colors[i % len(colors)]),
                    name=schedule.vessel.name,
                    hovertemplate=f"<b>{schedule.vessel.name}</b><br>" +
                                f"期間: {start.strftime('%m/%d')} - {end.strftime('%m/%d')}<br>" +
                                f"貨物量: {schedule.vessel.total_quantity:,}t<br>" +
                                f"コスト: ¥{schedule.total_cost:,}<extra></extra>"
                ))
            
            fig.update_layout(
                title="バース使用スケジュール",
                xaxis_title="日付",
                yaxis_title="バース",
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_detail_data():
    """詳細データ表示"""
    st.header("📋 マスターデータ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏭 バース情報")
        berth_df = get_berth_data()
        st.dataframe(berth_df, use_container_width=True)
    
    with col2:
        st.subheader("🚢 船舶情報")
        vessel_df = get_vessel_data()
        st.dataframe(vessel_df, use_container_width=True)

if __name__ == "__main__":
    main()
