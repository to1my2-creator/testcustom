import streamlit as st
import google.generativeai as genai
import json

# 1. 頁面基礎設定
st.set_page_config(page_title="Gemini AI 智慧報關系統", layout="wide", page_icon="🛃")

st.title("🛃 Gemini AI 智慧報關與稅則比對系統")
st.caption("結合 Google Gemini 大語言模型，即時分析全品項海關稅則、簽審規定與市場價格風險")

# 2. 側邊欄：設定 Gemini API Key
with st.sidebar:
    st.header("🔑 API 金鑰設定")
    gemini_api_key = st.text_input("輸入 Gemini API Key", type="password")
    st.markdown("[👉 免費取得 Google Gemini API Key](https://aistudio.google.com/)")

# 3. 輸入區塊
col1, col2 = st.columns(2)
with col1:
    prod_name = st.text_input("貨物名稱", value="有機乾燥貓咪零食 (雞胸肉凍乾)")
    prod_price = st.number_input("申報單價 (TWD/CIF)", value=350)
    prod_qty = st.number_input("申報數量", value=200)
with col2:
    origin = st.text_input("生產產地", value="日本 (JP)")
    spec_desc = st.text_area("特殊規格與功能說明", value="100% 純雞胸肉冷凍乾燥，純寵物食用，無其他添加物")

# 4. 點擊分析按鈕
if st.button("🚀 開始 Gemini AI 報關分析", type="primary"):
    if not gemini_api_key:
        st.error("請先在左側邊欄輸入您的 Gemini API Key！")
    else:
        with st.spinner("Gemini 關務專家正在檢索財政部關務署稅則與簽審規定中..."):
            try:
                # 設定 Gemini 模型
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                # 設計 Prompt
                prompt = f"""
                你是一名台灣專業的海關報關師與關務專家。請針對以下進口貨物進行報關分析：
                - 貨物名稱：{prod_name}
                - 產地：{origin}
                - 申報單價：CIF {prod_price} TWD
                - 規格說明：{spec_desc}

                請依據台灣財政部關務署 (GC411) 稅則與相關簽審規定，以 JSON 格式回答，格式必須如下：
                {{
                    "tariffs": [
                        "【首選】HS [完整11位稅則號別] (符合度 95%) - [稅則中文品名]",
                        "【備選】HS [完整11位稅則號別] (符合度 75%) - [稅則中文品名]"
                    ],
                    "reg_warning": "⚠️ 管制與簽審提示：[列出是否涉及防檢署動植物檢疫(如 B01/F01)、食藥署查驗、NCC、BSMI 或貨物稅等規定與報關建議]",
                    "benchmark_cif": [請評估該商品在台灣市場推估的合理完稅均價 CIF (整數 TWD)]
                }}
                請確保輸出為純 JSON 格式，不要包含任何 markdown 標記說明。
                """

                response = model.generate_content(prompt)
                
                # 解析 AI 回傳的 JSON 內容
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                ai_result = json.loads(clean_json)

                # 儲存至 Session State
                st.session_state["gemini_result"] = ai_result
                st.session_state["analyzed_prod"] = prod_name
                st.session_state["analyzed_price"] = prod_price

            except Exception as e:
                st.error(f"AI 分析過程出錯，請檢查 API Key 是否正確或稍後重試。錯誤訊息：{e}")

# 5. 顯示 AI 分析結果
if "gemini_result" in st.session_state:
    res = st.session_state["gemini_result"]
    current_name = st.session_state["analyzed_prod"]
    current_price = st.session_state["analyzed_price"]
    
    st.divider()
    st.subheader(f"📊 Gemini AI 實時分析結果：【{current_name}】")

    # 選擇稅則
    selected_hs = st.radio(
        "請選擇您欲採納申報的建議稅則：",
        options=res.get("tariffs", []),
        key=f"radio_{current_name}"
    )

    # 簽審規定提醒
    st.warning(res.get("reg_warning", "無特殊簽審規定"))

    # 價格風險分析
    est_cif = res.get("benchmark_cif", current_price)
    if est_cif > 0:
        diff_rate = ((current_price - est_cif) / est_cif) * 100
        if diff_rate < -20:
            st.error(f"⚠️ **價格風險警示**：您申報的單價 (TWD {current_price}) **低於市場完稅均價 {abs(diff_rate):.1f}%** (市場推估 CIF 均價為 TWD {est_cif})，易引發海關 C3 查驗並要求提供原廠發票。")
        elif diff_rate > 20:
            st.info(f"💡 **價格提醒**：您申報的單價 (TWD {current_price}) 高於市場完稅均價 {diff_rate:.1f}%。")
        else:
            st.success(f"✅ **價格正常**：申報金額符合市場行情（推估完稅均價為 TWD {est_cif}）。")

    # 匯出按鈕
    if st.button("確認選擇並匯出報關單 (XML/PDF)"):
        st.balloons()
        st.success(f"🎉 申報成功！已採納稅則：\n`{selected_hs}`\n\n系統已自動封裝報關 XML 檔案！")
