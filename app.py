import streamlit as st
import json
import os
import pandas as pd

# --- 1. 界面样式定制 (地缘战略指挥中心风格) ---
st.set_page_config(page_title="GSS 地缘战略指挥系统", layout="wide")

st.markdown("""
    <style>
    /* 全局背景：深海蓝色 */
    .stApp { 
        background-color: #0A192F; 
        color: #FFFFFF !important; 
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* 强制所有文字颜色为白色 */
    h1, h2, h3, p, span, label, .stMarkdown { color: #FFFFFF !important; }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] { background-color: #050C1A; border-right: 1px solid #303E50; }

    /* 按钮样式 (包含普通按钮 + 下载按钮) */
    div.stButton > button, div.stDownloadButton > button { 
        background-color: #112240 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #E9C46A !important; 
        border-radius: 4px;
        font-weight: bold; 
        width: 100%;
    }
    
    div.stButton > button:hover, div.stDownloadButton > button:hover { 
        background-color: #E9C46A !important; 
        color: #0A192F !important; 
        border: 1px solid #FFFFFF !important;
    }
    
    /* 强制鼠标悬停时内部文字变黑 */
    div.stButton > button:hover p, div.stDownloadButton > button:hover p,
    div.stButton > button:hover span, div.stDownloadButton > button:hover span {
        color: #0A192F !important;
    }

    /* Subheader 样式微调：更紧凑、战术金颜色 */
    [data-testid="stSubheader"] {
        font-size: 1.1rem !important;
        color: #E9C46A !important;
        border-bottom: 1px solid #1B3A57;
        padding-bottom: 5px;
        letter-spacing: 1px;
    }

    [data-testid="stHeader"] {
        display: none !important;
    }

    /* Dropzone (黑底，白虚线边) */
    [data-testid="stFileUploadDropzone"] {
        background-color: #0A192F !important;
        border: 2px dashed #FFFFFF !important;
        border-radius: 6px !important;
    }

    /* 强制内部提示文字为黑色 */
    [data-testid="stFileUploadDropzone"] div,
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] small {
        color: #0A192F !important;
    }



    /* 选项卡 (Tabs) 样式修正 */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important; 
        background-color: #112240;
        border-radius: 4px 4px 0 0;
        margin-right: 5px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #FFFFFF !important; 
    }
    /* 核心：选中时文字与图标旁边的段落强制变黑 */
    .stTabs [aria-selected="true"] p, 
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div {
        color: #000000 !important; 
        font-weight: bold;
    }

    /* 输入框样式 */
    input { background-color: #112240 !important; color: #FFFFFF !important; border: 1px solid #303E50 !important; }
    
    /* 紧凑型领土卡片 */
    .territory-card {
        background-color: #112240; border-left: 3px solid #E9C46A;
        padding: 6px 10px; margin-bottom: 5px; border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 存档逻辑与核心数据 ---
SAVE_FILE = "gss_website_save.json"
LAND_BONUS = {
    'A1': {'g': 3}, 'A2': {'o': 2}, 'A3': {'o': 5}, 'A4': {'o': 3}, 'A5': {'g': 5},
    'A6': {'s': 3}, 'A7': {'s': 3}, 'A8': {'g': 3}, 'B1': {'s': 3}, 'B2': {'s': 4},
    'B3': {'o': 3}, 'B4': {'g': 5}, 'C1': {'o': 4}, 'C2': {'o': 3}, 'C3': {'s': 4},
    'C4': {'g': 3}, 'D1': {'o': 5}, 'D2': {'o': 6}, 'D3': {'o': 3}, 'D4': {'o': 3},
    'E1': {'o': 3}, 'E2': {'s': 3}, 'E3': {'s': 4}, 'E4': {'g': 5}, 'F1': {'g': 2},
    'F2': {'g': 5}, 'F3': {'o': 3}, 'F4': {'s': 4}, 'G1': {'s': 3}, 'G2': {'g': 4}
}

def save_data():
    """保存当前所有 session_state 到本地文件"""
    data = {
        't': st.session_state.t,
        'clist': st.session_state.clist,
        'dict_land': st.session_state.dict_land,
        'dict_gold': st.session_state.dict_gold,
        'dict_oil': st.session_state.dict_oil,
        'dict_steel': st.session_state.dict_steel,
        'dict_people': st.session_state.dict_people,
        'dict_action': st.session_state.dict_action,
        'dict_ceasefire': st.session_state.dict_ceasefire,
        'logs': st.session_state.logs,
        'country_deploy': st.session_state.country_deploy, 
        'land_deploy':  st.session_state.land_deploy
    }
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    """从本地文件读取存档"""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            st.session_state.update(data)
        return True
    return False

# --- 3. 逻辑初始化 ---
if 'initialized' not in st.session_state:
    if not load_data():
        st.session_state.update({
            't': 0, 'clist': [], 'dict_land': {}, 'dict_gold': {}, 
            'dict_oil': {}, 'dict_steel': {}, 'dict_people': {}, 
            'dict_action': {}, 'dict_ceasefire': {}, 'logs': [],
            'country_deploy': {}, 'land_deploy': {} 
        })
    st.session_state.initialized = True

def add_log(msg):
    st.session_state.logs.insert(0, f"[Round {st.session_state.t}] {msg}")

def calculate_score(c):
    land_v = len(st.session_state.dict_land[c]) * 20
    gold_v = st.session_state.dict_gold[c]
    oil_v = st.session_state.dict_oil.get(c, 0) * 1.25
    steel_v = st.session_state.dict_steel.get(c, 0) * 2
    ap_v = st.session_state.dict_action.get(c, 0) * 10
    return int(land_v + gold_v + oil_v + steel_v + ap_v)

# --- 4. 侧边栏控制 ---
with st.sidebar:
    st.title("🛰️ 战略控制台")

    # === 云端专属：手动上传与下载存档 ===
    st.divider()
    st.markdown("### ☁️ 云端存档管理")
    
    # 1. 下载当前存档到本地电脑
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as file:
            st.download_button(
                label="⬇️ 导出今日存档",
                data=file,
                file_name=f"gss_backup_T{st.session_state.t}.json",
                mime="application/json"
            )
            
    # 2. 从本地电脑恢复存档
    uploaded_file = st.file_uploader("⬆️ 恢复历史存档", type="json")
    if uploaded_file is not None:
        if st.button("⚠️ 确认覆盖并恢复数据"):
            data = json.load(uploaded_file)
            st.session_state.update(data)
            save_data() # 将上传的数据写回服务器的 json
            st.success("✅ 存档恢复成功！")
            st.rerun()
    st.divider()

    st.button("💾 保存当前进度", on_click=save_data)
    st.success("当前进度已保存")
    
    if st.session_state.t == 0 and not st.session_state.clist:
        c_in = st.text_input("输入国家名（用英文逗号隔开）", "A, B, C, D")
        if st.button("📡 初始化推演系统"):
            names = [x.strip().upper() for x in c_in.split(',') if x.strip()]
            st.session_state.clist = names
            for c in names:
                st.session_state.dict_gold[c], st.session_state.dict_land[c] = 30, []
                st.session_state.dict_oil[c], st.session_state.dict_steel[c] = 0, 0
                st.session_state.dict_people[c], st.session_state.dict_action[c] = 0, 0
            save_data()
            st.rerun()
    st.divider()
    if st.button("⚠️ 重置所有进度"):
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
        st.session_state.clear(); st.rerun()

# --- 5. 主大屏渲染 ---
st.title(f"第 {st.session_state.t} 回合")

if not st.session_state.clist:
    st.info("系统待命。请在侧边栏初始化国家数据以启动。")
    st.stop()

# 实力看板
score_cols = st.columns(len(st.session_state.clist))
for i, c in enumerate(st.session_state.clist):
    with score_cols[i]:
        score = calculate_score(c)
        st.metric(f"国家 {c}", f"{score} PTS")
        st.progress(min(score/300, 1.0))

st.divider()


left_col, right_col = st.columns([3, 1])

with right_col:
    st.markdown('<p style="font-size:24px; font-weight:bold; color:white;">领土监控</p>', unsafe_allow_html=True)
    for c in st.session_state.clist:
        lands = st.session_state.dict_land[c]
        st.markdown(f"""<div class="territory-card"><strong>{c} 国 ({len(lands)})</strong><br><small>{'|'.join(lands) if lands else "无领土"}</small></div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown('<p style="font-size:24px; font-weight:bold; color:white;">推演日志</p>', unsafe_allow_html=True)
    for l in st.session_state.logs[:12]: st.caption(l)

with left_col:
    tab_m, tab_deploy, tab_d, tab_s = st.tabs(["⚔️ 军事推演", "🏃‍兵力部署","🤝 外交博弈", "💰 资源核算"])

    with tab_deploy:
        if st.session_state.t == 0:
            st.info("第 0 回合为领土划分阶段，暂无需进行战力部署。")
        else:
            st.subheader("🛡️ 全球战力部署中心")
            dep_c = st.selectbox("请选择要部署的国家", st.session_state.clist)
            
            lands = st.session_state.dict_land[dep_c]
            if not lands:
                st.warning(f"{dep_c} 国已失去所有领土，无法部署。")
            else:
                total_power = st.session_state.dict_people[dep_c]
                st.markdown(f"**{dep_c} 国拥有总战力：<span style='color:#E9C46A; font-size:1.2rem;'>{total_power}</span> 点**", unsafe_allow_html=True)
                
                # 使用一个容器来包裹输入框，并实时计算当前已分配总数
                dep_inputs = {}
                current_sum = 0
                
                cols = st.columns(3) # 排版：每行显示3个地块的输入框
                for idx, l in enumerate(lands):
                    with cols[idx % 3]:
                        # 限制最小值必须为1，强制满足“已有领土必须至少保留1战力”
                        # 如果之前已经部署过，读取之前的值，否则默认为1
                        default_val = st.session_state.country_deploy.get(dep_c, {}).get(l, 1)
                        val = st.number_input(f"📍 地块 {l}", min_value=1, value=default_val, step=1, key=f"dep_{dep_c}_{l}")
                        dep_inputs[l] = val
                        current_sum += val
                
                # 实时进度与校验提示
                st.divider()
                if current_sum == total_power:
                    st.success(f"✅ 分配成功！已分配: {current_sum} / {total_power}")
                elif current_sum > total_power:
                    st.error(f"❌ 超出上限！已分配: {current_sum} / {total_power}")
                else:
                    st.warning(f"⚠️ 战力未用完！已分配: {current_sum} / {total_power}")
                
                # 确认按钮
                if st.button("🔒 锁定并下达部署指令"):
                    if current_sum != total_power:
                        st.error(f"部署错误：战力总数不对！{dep_c} 分配了 {current_sum} 点，但必须正好等于 {total_power} 点。")
                    else:
                        st.session_state.country_deploy[dep_c] = dep_inputs
                        st.session_state.land_deploy.update(dep_inputs)
                        add_log(f"{dep_c} 完成了战力部署：{dep_inputs}")
                        save_data() # 存档
                        st.success(f"指令已确认！{dep_c} 国完成部署。")

    with tab_m:
        if st.session_state.t == 0:
            # 1. 初始化并行的轮次状态
            if 'setup_phase' not in st.session_state:
                st.session_state.setup_phase = 1              # 记录当前是第几轮 (1~3)
            if 'claimed_this_round' not in st.session_state:
                st.session_state.claimed_this_round = []      # 记录这轮谁已经占领过了

            if st.session_state.setup_phase <= 3:
                st.subheader(f"🏁 初始领土划分 - 第 {st.session_state.setup_phase} 轮 / 共 3 轮")
                
                # 获取全局已被占领的领土，防冲突参考
                all_claimed_lands = [l for lands in st.session_state.dict_land.values() for l in lands]
                if all_claimed_lands:
                    st.caption(f"已被占领地块: {', '.join(all_claimed_lands)}")
                
                # 筛选出本轮还没按确认的国家
                remaining_countries = [c for c in st.session_state.clist if c not in st.session_state.claimed_this_round]
                
                if remaining_countries:
                    # 动态生成列数，有人确认了列数就会变少，实现“消失”效果
                    cols = st.columns(len(remaining_countries))
                    
                    for idx, c in enumerate(remaining_countries):
                        with cols[idx]:
                            st.markdown(f"**{c} 国**")
                            # 录入当前国家的选择
                            land_input = st.text_input("目标地块编号", key=f"draft_{st.session_state.setup_phase}_{c}").strip().upper()
                            
                            if st.button(f"🚩 确认占领 ({c})", key=f"btn_{st.session_state.setup_phase}_{c}"):
                                if not land_input:
                                    st.error("⚠️ 不能为空！")
                                elif land_input in all_claimed_lands:
                                    st.error(f"❌ 冲突！{land_input} 已经被捷足先登。")
                                else:
                                    # 校验通过，执行占领与扣费
                                    st.session_state.dict_land[c].append(land_input)
                                    st.session_state.dict_gold[c] -= 10
                                    
                                    # 把这个国家加入“本轮已完结”名单
                                    st.session_state.claimed_this_round.append(c)
                                    add_log(f"T0 (第{st.session_state.setup_phase}轮): {c} 抢占了 {land_input}")
                                    
                                    save_data() # 进度存档
                                    st.rerun()  # 刷新页面，该国家输入框消失
                else:
                    # 当 remaining_countries 为空时，说明所有人都按了确认
                    st.success(f"✅ 所有参演国已完成第 {st.session_state.setup_phase} 轮部署！")
                    
                    if st.session_state.setup_phase < 3:
                        if st.button("➡️ 开启下一轮占领"):
                            st.session_state.setup_phase += 1
                            st.session_state.claimed_this_round = [] # 清空名单，新一轮开始
                            save_data()
                            st.rerun()
                    else:
                        if st.button("🏁 结算初始资源，正式进入第 1 回合"):
                            st.session_state.t = 1
                            for c in st.session_state.clist:
                                # 1. 自动计算该国已占领土地的 Bonus
                                ls = st.session_state.dict_land[c]
                                gb, ob, sb = 0, 0, 0
                                for l in ls:
                                    b = LAND_BONUS.get(l, {})
                                    gb += b.get('g', 0)
                                    ob += b.get('o', 0)
                                    sb += b.get('s', 0)
                                
                                # 2. 发放 T1 固定的初始战力与行动点
                                st.session_state.dict_action[c] = 2
                                st.session_state.dict_people[c] = 10
                                
                                # 3. 黄金 = 第 0 回合买地剩下的钱 + 土地黄金 Bonus
                                st.session_state.dict_gold[c] += gb
                                
                                # 4. 石油/钢铁 = 基础产量(领土数*2 或 *1) + 土地石油/钢铁 Bonus
                                st.session_state.dict_oil[c] = len(ls) * 2 + ob
                                st.session_state.dict_steel[c] = len(ls) + sb
                                
                            save_data()
                            st.rerun()
        else:
            st.subheader("⚔️ 战术指令控制台")
            active_c = st.selectbox("当前下达指令方", st.session_state.clist)
            m_type = st.radio("行动类型", ["移动", "进攻"], horizontal=True)
            
            # 第一排输入：地块与战力
            c1, c2, c3 = st.columns(3)
            f_l = c1.text_input("移出地/发起地").upper().strip()
            t_l = c2.text_input("目标地块").upper().strip()
            # 读取该出发地的现有战力，用于限制输入最大值
            current_ppl = st.session_state.country_deploy.get(active_c, {}).get(f_l, 0) if f_l else 0
            troop_count = c3.number_input(f"出动战力 (当前: {current_ppl})", min_value=1, max_value=5, value=1)
            
            # 第二排输入：环境与裁判判定
            c4, c5 = st.columns(2)
            sea = c4.checkbox("跨海行动")
            in_range = c5.checkbox("判定：在有效范围(1格)内", value=True)
            
            st.divider()
            
            if st.button("🔥 锁定并执行指令"):
                if not f_l or not t_l:
                    st.error("⚠️ 请输入完整的发起地和目标地编号！")
                elif f_l not in st.session_state.dict_land[active_c]:
                    st.error(f"❌ 非法出发地：{f_l} 不属于 {active_c}，无法调动战力！")
                elif current_ppl <= 1 or troop_count >= current_ppl:
                    st.error(f"❌ 战力不足：{f_l} 现有 {current_ppl} 战力，必须保留至少 1 个单位防守本国领土！")
                else:
                    # ================= 移动逻辑 =================
                    if m_type == "移动":
                        ap_cost = 4 if sea else 2
                        if st.session_state.dict_action[active_c] < ap_cost:
                            st.error(f"❌ 行动点数不足：剩余 {st.session_state.dict_action[active_c]}，需要 {ap_cost}。")
                        else:
                            # 判定目标地块归属
                            target_owner = None
                            for c in st.session_state.clist:
                                if t_l in st.session_state.dict_land[c]:
                                    target_owner = c
                                    break
                            
                            if target_owner and target_owner != active_c:
                                st.error(f"❌ 移动失败：{t_l} 已被 {target_owner} 占领！进入该地请使用「进攻」指令。")
                            else:
                                # 扣除AP
                                st.session_state.dict_action[active_c] -= ap_cost
                                
                                if not in_range:
                                    st.error(f"❌ 超出移动范围！行动失败，但仍扣除行动点数 {ap_cost}。")
                                else:
                                    # 执行移动更新
                                    st.session_state.country_deploy[active_c][f_l] -= troop_count
                                    st.session_state.country_deploy[active_c][t_l] = st.session_state.country_deploy[active_c].get(t_l, 0) + troop_count
                                    
                                    # 若是新领土，加入版图
                                    if t_l not in st.session_state.dict_land[active_c]:
                                        st.session_state.dict_land[active_c].append(t_l)
                                    
                                    # 更新全局战力分布
                                    st.session_state.land_deploy[f_l] = st.session_state.country_deploy[active_c][f_l]
                                    st.session_state.land_deploy[t_l] = st.session_state.country_deploy[active_c][t_l]
                                    
                                    add_log(f"{active_c} 移动 {troop_count} 战力: {f_l} ➔ {t_l}")
                                    st.success(f"✅ 移动成功！消耗 {ap_cost} 行动点数。")
                                save_data()

                    # ================= 进攻逻辑 =================
                    elif m_type == "进攻":
                        if t_l in st.session_state.dict_land[active_c]:
                            st.error(f"❌ {t_l} 已经是你自己的领土了！")
                        else:
                            ap_cost = 2 if sea else 1
                            oil_cost = 4 if sea else 2
                            steel_cost = 2 if sea else 1
                            
                            if (st.session_state.dict_action[active_c] < ap_cost or 
                                st.session_state.dict_oil[active_c] < oil_cost or 
                                st.session_state.dict_steel[active_c] < steel_cost):
                                st.error(f"❌ 战争资源不足！需要行动点数:{ap_cost}, 油:{oil_cost}, 铁:{steel_cost}")
                            else:
                                # 获取防守方
                                defender = None
                                for c in st.session_state.clist:
                                    if t_l in st.session_state.dict_land[c]:
                                        defender = c
                                        break
                                        
                                # 校验停战协议 (在扣除资源前拦截，体验更好)
                                if defender:
                                    pair = f"{min(active_c, defender)}-{max(active_c, defender)}"
                                    if pair in st.session_state.dict_ceasefire and st.session_state.t <= st.session_state.dict_ceasefire[pair]:
                                        st.error(f"🛑 行动受阻：{active_c} 与 {defender} 处于强制停战期（至 T{st.session_state.dict_ceasefire[pair]}）！行动被国际法撤回。")
                                        st.stop()

                                # 扣除战争资源
                                st.session_state.dict_action[active_c] -= ap_cost
                                st.session_state.dict_oil[active_c] -= oil_cost
                                st.session_state.dict_steel[active_c] -= steel_cost
                                
                                if not in_range:
                                    st.error(f"❌ 攻击偏离！目标超出打击范围，消耗了资源但未能交火。")
                                else:
                                    # --- 战斗结算 ---
                                    defend_ppl = st.session_state.land_deploy.get(t_l, 0)
                                    
                                    if troop_count > defend_ppl:
                                        # 进攻胜利
                                        if defender:
                                            st.session_state.dict_land[defender].remove(t_l)
                                            st.session_state.country_deploy[defender].pop(t_l, None)
                                            
                                        st.session_state.dict_land[active_c].append(t_l)
                                        st.session_state.country_deploy[active_c][t_l] = troop_count
                                        st.session_state.country_deploy[active_c][f_l] -= troop_count
                                        
                                        st.session_state.land_deploy[f_l] = st.session_state.country_deploy[active_c][f_l]
                                        st.session_state.land_deploy[t_l] = troop_count
                                        
                                        add_log(f"{active_c} 战胜 {defender if defender else '野怪'}，夺取 {t_l}")
                                        st.success(f"🏆 进攻胜利！{active_c} 以 {troop_count} VS {defend_ppl} 的优势占领了 {t_l}。")
                                        
                                    elif defend_ppl > troop_count:
                                        # 进攻失败
                                        st.session_state.country_deploy[active_c][f_l] -= troop_count
                                        st.session_state.land_deploy[f_l] = st.session_state.country_deploy[active_c][f_l]
                                        
                                        add_log(f"{active_c} 强攻 {t_l} 失败，{troop_count} 战力全军覆没")
                                        st.error(f"💀 惨败！{active_c} 进攻部队（{troop_count}人）被防守方（{defend_ppl}人）全歼！")
                                        
                                    else:
                                        # 平局
                                        add_log(f"{active_c} 强攻 {t_l} 陷入僵局，部队退回")
                                        st.warning(f"⚔️ 平局！双方（{troop_count} VS {defend_ppl}）势均力敌，进攻方退回原籍，无伤亡。")
                                        
                                save_data()

    with tab_d:
        # 规则提醒：最后一轮（通常是第8轮）不进行谈判
        if st.session_state.t >= 8:
            st.error("🚨 警告：推演进入最终阶段，所有外交窗口已强制关闭。")
        else:         
            # 使用两列布局，左侧签署协议，右侧查看状态
            dip_col1, dip_col2 = st.columns([2, 1])
            
            with dip_col1:
                neg_type = st.radio("协议类别", ["物资贸易", "停战协议"], horizontal=True)
                
                c1 = st.selectbox("发起方 (Country A)", st.session_state.clist, key="dip_c1")
                c2 = st.selectbox("接受方 (Country B)", st.session_state.clist, key="dip_c2")
                
                if c1 == c2:
                    st.warning("请选择两个不同的国家进行谈判。")
                else:
                    if neg_type == "物资贸易":
                        st.info(f"正在拟定：{c1} 与 {c2} 的贸易协定")
                        
                        # 左右对开：A给出的资源 vs B给出的资源
                        trade_a, trade_b = st.columns(2)
                        with trade_a:
                            st.write(f"📤 {c1} 给出的物资")
                            g_a = st.number_input(f"{c1} 黄金", min_value=0, key="ga")
                            o_a = st.number_input(f"{c1} 石油", min_value=0, key="oa")
                            s_a = st.number_input(f"{c1} 钢铁", min_value=0, key="sa")
                        with trade_b:
                            st.write(f"📥 {c2} 给出的物资")
                            g_b = st.number_input(f"{c2} 黄金", min_value=0, key="gb")
                            o_b = st.number_input(f"{c2} 石油", min_value=0, key="ob")
                            s_b = st.number_input(f"{c2} 钢铁", min_value=0, key="sb")
                        
                        if st.button("🛰️ 签署并执行贸易协定"):
                            # 资源校验
                            if (st.session_state.dict_gold[c1] < g_a or st.session_state.dict_oil[c1] < o_a or 
                                st.session_state.dict_steel[c1] < s_a):
                                st.error(f"❌ {c1} 资源余额不足，无法履行协议。")
                            elif (st.session_state.dict_gold[c2] < g_b or st.session_state.dict_oil[c2] < o_b or 
                                st.session_state.dict_steel[c2] < s_b):
                                st.error(f"❌ {c2} 资源余额不足，无法履行协议。")
                            else:
                                st.success("当前进度已保存")
                                # 执行资源互换
                                st.session_state.dict_gold[c1] += (g_b - g_a)
                                st.session_state.dict_oil[c1] += (o_b - o_a)
                                st.session_state.dict_steel[c1] += (s_b - s_a)
                                
                                st.session_state.dict_gold[c2] += (g_a - g_b)
                                st.session_state.dict_oil[c2] += (o_a - o_b)
                                st.session_state.dict_steel[c2] += (s_a - s_b)

                                add_log(f"贸易: {c1} 与 {c2} 完成物资互换。")
                                save_data() # 存档
                                st.rerun()            

                    elif neg_type == "停战协议":
                        st.info(f"🕊️ 正在签署：{c1} 与 {c2} 的三年停战协议")
                        st.write("注：停战协定一旦签署，未来 3 回合内由系统强制执行，不可撕毁。")
                        
                        if st.button("✍️ 签署强制停战令"):
                            pair = tuple(sorted([c1, c2]))
                            pair_key = f"{pair[0]}-{pair[1]}"
                            expire_t = st.session_state.t + 3 # 停战3回合
                            st.session_state.dict_ceasefire[pair_key] = expire_t
                            
                            add_log(f"停战: {c1} 与 {c2} 签署和平协议，直至第 {expire_t} 回合。")
                            st.success(f"🕊️ 协议签署成功！第 {expire_t} 回合前禁止互相进攻。")
                            st.rerun()

            with dip_col2:
                st.markdown('<p style="font-size:24px; font-weight:bold; color:white;">当前生效协议</p>', unsafe_allow_html=True)
                if not st.session_state.dict_ceasefire:
                    st.caption("暂无生效的和平协议。")
                else:
                    for pair, expire in st.session_state.dict_ceasefire.items():
                        # 检查协议是否过期
                        if st.session_state.t <= expire:
                            st.warning(f"🏳️ {pair} (有效期至 T{expire})")
                        else:
                            st.caption(f"⌛ {pair} (协议已到期)")
    

    with tab_s:
        st.subheader("资源明细与回合结算")
        
        # 1. 资源统计表
        res_df = pd.DataFrame({
            "国家": st.session_state.clist,
            "行动点数": [st.session_state.dict_action[c] for c in st.session_state.clist],
            "黄金": [st.session_state.dict_gold[c] for c in st.session_state.clist],
            "石油": [st.session_state.dict_oil[c] for c in st.session_state.clist],
            "钢铁": [st.session_state.dict_steel[c] for c in st.session_state.clist],
            "战力": [st.session_state.dict_people[c] for c in st.session_state.clist],
            "土地总数": [len(st.session_state.dict_land[c]) for c in st.session_state.clist]
        })
        st.table(res_df)
        
        # 2. 行动点数兑换模块 (仅在 1-8 回合显示)
        if st.session_state.t > 0 and st.session_state.t <= 8:
            st.divider()
            st.subheader("⚡ 行动点数兑换中心")
            st.info("兑换比例：1行动点数 = 10 黄金 / 8 石油 / 5 钢铁。未兑换的行动点数将在回合结束时自动清零。")
            
            ex_c = st.selectbox("请选择要进行兑换的国家", st.session_state.clist)
            rem_ap = st.session_state.dict_action.get(ex_c, 0)
            
            if rem_ap <= 0:
                st.warning(f"账户提示：{ex_c} 国行动点已耗尽，无需兑换。")
            else:
                st.markdown(f"**{ex_c} 国当前拥有 <span style='color:#E9C46A; font-size:1.2rem;'>{rem_ap}</span> 点剩余行动点**", unsafe_allow_html=True)
                
                # 使用三个并排的数字输入框，让玩家分配 AP
                ex1, ex2, ex3 = st.columns(3)
                to_gold = ex1.number_input("投入行动点数兑换 黄金", min_value=0, max_value=rem_ap, value=0, step=1, key=f"ex_g_{ex_c}")
                to_oil = ex2.number_input("投入行动点数兑换 石油", min_value=0, max_value=rem_ap, value=0, step=1, key=f"ex_o_{ex_c}")
                to_steel = ex3.number_input("投入行动点数兑换 钢铁", min_value=0, max_value=rem_ap, value=0, step=1, key=f"ex_s_{ex_c}")
                
                total_ex = to_gold + to_oil + to_steel
                
                if total_ex > rem_ap:
                    st.error(f"❌ 数量错误！你试图兑换的行动点数总和（{total_ex}）超出了该国拥有的上限（{rem_ap}）。")
                elif total_ex > 0:
                    if st.button(f"🔄 确认执行兑换 ({ex_c})"):
                        # 执行扣除与资源增加
                        st.session_state.dict_action[ex_c] -= total_ex
                        g_earn, o_earn, s_earn = to_gold * 10, to_oil * 8, to_steel * 5
                        
                        st.session_state.dict_gold[ex_c] += g_earn
                        st.session_state.dict_oil[ex_c] += o_earn
                        st.session_state.dict_steel[ex_c] += s_earn
                        
                        add_log(f"兑换: {ex_c} 消耗 {total_ex} 行动点数，获得 {g_earn}G, {o_earn}O, {s_earn}S")
                        save_data()
                        st.success(f"✅ 兑换成功！{ex_c} 的国库资源已更新。")
                        st.rerun()
        
        st.divider()
        
        # 3. 回合结束与结算逻辑
        if st.button("⌛ 结束本轮推演并进入下一回合 (将自动清零未用行动点数)"):
            # 废弃未使用的 AP，将其清零（替代了之前的强制换金币逻辑）
            for c in st.session_state.clist:
                st.session_state.dict_action[c] = 0
            
            # 回合更迭与资源再生
            st.session_state.t += 1
            if st.session_state.t <= 8:
                for c in st.session_state.clist:
                    ls = st.session_state.dict_land[c]
                    gb, ob, sb = 0, 0, 0
                    for l in ls:
                        b = LAND_BONUS.get(l, {})
                        gb += b.get('g', 0); ob += b.get('o', 0); sb += b.get('s', 0)
                    
                    st.session_state.dict_gold[c] += (gb + st.session_state.dict_people[c])
                    st.session_state.dict_oil[c], st.session_state.dict_steel[c] = len(ls)*2 + ob, len(ls) + sb
                    st.session_state.dict_action[c] = len(ls)
                    
                    p = st.session_state.dict_people[c]
                    st.session_state.dict_people[c] += 1 if p >= 10 else int((10-p)*0.5 + 2)
            save_data()
            st.rerun()