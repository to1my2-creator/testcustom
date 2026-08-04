import streamlit as st

# 1. 頁面基礎設定
st.set_page_config(page_title="AI 智慧報關系統 (測試版)", layout="wide", page_icon="🛃")

st.title("🛃 AI 智慧報關與稅則比對系統 (Demo 測試版)")
st.caption("免 API Key！內建動態關務資料庫與智慧風險分析引擎，即時測試稅則比對、簽審提醒與價格風險")

# 2. 本機內建關務資料庫
CUSTOMS_KNOWLEDGE_BASE = {
    "貓": {
        "tariffs": [
            "【首選】HS 2309.10.00.00-2 (符合度 95.0%) - 貓狗食品，零售包裝者",
            "【備選】HS 0511.99.90.90-9 (符合度 70.0%) - 其他未列名動物產品"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：含肉類成分寵物食品涉 **農業部防檢署動植物檢疫 (B01)**，須檢附輸出國檢疫證明書；涉 **食藥署輸入查驗 (F01)**。",
        "benchmark_cif": 380
    },
    "耳機": {
        "tariffs": [
            "【首選】HS 8518.30.00.00-8 (符合度 94.5%) - 頭戴/塞耳式耳機",
            "【備選】HS 8517.62.00.00-5 (符合度 76.2%) - 其他接收轉換聲音器具"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品含藍牙模組涉 **NCC 電信管制**；內建鋰電池涉 **BSMI 商品檢驗**。",
        "benchmark_cif": 1680
    },
    "電視": {
        "tariffs": [
            "【首選】HS 8528.72.00.00-3 (符合度 92.1%) - 彩色液晶電視機",
            "【備選】HS 8528.52.00.00-0 (符合度 71.0%) - 其他監視器"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品涉 **BSMI 驗證登錄** (安規/能源效率) 及 **貨物稅 (13%)**。",
        "benchmark_cif": 9000
    },
    "手機": {
        "tariffs": [
            "【首選】HS 8517.13.00.00-0 (符合度 98.0%) - 智慧型手機",
            "【備選】HS 8517.18.00.00-5 (符合度 60.0%) - 其他電話機"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品涉及 **NCC 型式認證**，進口需檢附電信管制射頻器材進口許可證。",
        "benchmark_cif": 12000
    },
    "電腦": {
        "tariffs": [
            "【首選】HS 8471.30.00.00-8 (符合度 95.0%) - 可攜式自動資料處理機 (筆記型電腦)",
            "【備選】HS 8471.41.00.00-5 (符合度 80.0%) - 其他自動資料處理機"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品涉及 **BSMI 電磁相容 (EMC) 與安規檢驗**。",
        "benchmark_cif": 21000
    }
}

DEFAULT_KNOWLEDGE = {
    "tariffs": [
        "【首選】HS 9999.00.00.00-0 (符合度 85.0%) - 一般進口貨品歸類稅則",
        "【備選】HS 8479.89.99.00-9 (符合度 65.0%) - 其他具有獨立功能之機械器具"
    ],
    "reg_warning": "ℹ️ **管制與簽審提示**：請依海關關港貿單一窗口查詢該特定貨品之輸出入規定代碼 (如 C02/F01/BSMI/NCC 等)。",
    "benchmark_cif": 5000
}

# 3. 輸入區塊
col1, col2 = st.columns(2)
with col1:
    prod_name = st.text_input("貨物名稱", value="有機乾燥貓咪零食 (雞胸肉凍乾)")
    prod_price = st.number_input("申報單價 (TWD/CIF)", value=350)
    prod_qty = st.number_input("申報數量", value=200)
with col2:
    origin = st.text_input("生產產地", value="日本 (JP)")
    spec_desc = st.text_area("特殊規格與功能說明", value="100% 純雞胸肉冷凍乾燥，純寵物食用，無其他添加物")

# 4. 分析按鈕
if st.button("🚀 開始智慧報關分析", type="primary"):
    st.session_state["analyzed_prod"] = prod_name
    st.session_state["analyzed_price"] = prod_price

# 5. 結果呈現
if "analyzed_prod" in st.session_state:
    current_name = st.session_state["analyzed_prod"]
    current_price = st.session_state["analyzed_price"]

    # 搜尋知識庫
    matched_data = DEFAULT_KNOWLEDGE
    for key, data in CUSTOMS_KNOWLEDGE_BASE.items():
        if key in current_name:
            matched_data = data
            break

    st.divider()
    st.subheader(f"📊 智慧分析結果：【{current_name}】")

    # 選擇稅則
    selected_hs = st.radio(
        "請選擇您欲採納申報的建議稅則：",
        options=matched_data["tariffs"],
        key=f"radio_{current_name}"
    )

    # 簽審提醒
    st.warning(matched_data["reg_warning"])

    # 價格風險分析
    est_cif = matched_data["benchmark_cif"]
    diff_rate = ((current_price - est_cif) / est_cif) * 100

    if diff_rate < -20:
        st.error(f"⚠️ **價格風險警示**：您申報的單價 (TWD {current_price}) **低於市場完稅均價 {abs(diff_rate):.1f}%** (推估 CIF 完稅均價為 TWD {est_cif})，易引發海關 C3 查驗並要求提供原廠發票。")
    elif diff_rate > 20:
        st.info(f"💡 **價格提醒**：您申報的單價 (TWD {current_price}) 高於市場完稅均價 {diff_rate:.1f}%。")
    else:
        st.success(f"✅ **價格正常**：申報金額符合市場行情（推估 CIF 完稅均價為 TWD {est_cif}）。")

    # 匯出按鈕
    if st.button("確認選擇並匯出報關單 (XML/PDF)"):
        st.balloons()
        st.success(f"🎉 申報成功！已採納稅則：\n`{selected_hs}`\n\n系統已自動封裝報關 XML 檔案！")
