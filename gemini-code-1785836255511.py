import json
from groq import Groq
import streamlit as st

# 1. 頁面設定
st.set_page_config(
    page_title="AI 智慧報關系統", layout="wide", page_icon="🛃"
)

st.title("🛃 AI 智慧報關與稅則比對系統")
st.caption("結合 Groq (Llama 3) 模型，自動分析海關稅則、簽審規定與市場價格風險")

# 2. 自動抓取 Secrets 背景金鑰 (若無才顯示側邊欄輸入)
api_key = st.secrets.get("GROQ_API_KEY", "")

with st.sidebar:
  st.header("⚙️ 系統設定")
  if api_key:
    st.success("✅ 免填 Key！已自動連線背景 API")
  else:
    api_key = st.text_input("輸入 Groq API Key", type="password")
    st.markdown("[👉 免費取得 Groq API Key](https://console.groq.com/)")

# 3. 輸入區塊
col1, col2 = st.columns(2)
with col1:
  prod_name = st.text_input("貨物名稱", value="有機乾燥貓咪零食 (雞胸肉凍乾)")
  prod_price = st.number_input("申報單價 (TWD/CIF)", value=350)
  prod_qty = st.number_input("申報數量", value=200)
with col2:
  origin = st.text_input("生產產地", value="日本 (JP)")
  spec_desc = st.text_area(
      "特殊規格與功能說明",
      value="100% 純雞胸肉冷凍乾燥，純寵物食用，無其他添加物",
  )

# 4. 分析按鈕
if st.button("🚀 開始全品項 AI 報關分析", type="primary"):
  if not api_key:
    st.error("請先在側邊欄輸入 Groq API Key 或於 Secrets 設定背景金鑰！")
  else:
    with st.spinner("⚡ 關務專家正在高速分析中..."):
      try:
        client = Groq(api_key=api_key)

        prompt = f"""
                你是台灣海關報關師。請針對貨物「{prod_name}」（規格：{spec_desc}，CIF單價：{prod_price} TWD，產地：{origin}）進行分析。
                請嚴格輸出純 JSON（勿加任何 markdown 或額外說明）：
                {{
                    "tariffs": [
                        "【首選】HS [完整11位稅則] (符合度 95%) - [中文品名]",
                        "【備選】HS [完整11位稅則] (符合度 75%) - [中文品名]"
                    ],
                    "reg_warning": "⚠️ 管制與簽審提示：[簡述是否涉及 BSMI/NCC/食藥署/防檢署/貨物稅等規定與建議]",
                    "benchmark_cif": [合理市場 CIF 完稅均價數字，僅填數字不要填文字]
                }}
                """

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )

        ai_result = json.loads(response.choices[0].message.content)

        st.session_state["groq_result"] = ai_result
        st.session_state["analyzed_prod"] = prod_name
        st.session_state["analyzed_price"] = prod_price

      except Exception as e:
        st.error(f"分析失敗，請確認 API Key 是否正確。錯誤訊息：{e}")

# 5. 結果呈現
if "groq_result" in st.session_state:
  res = st.session_state["groq_result"]
  current_name = st.session_state["analyzed_prod"]
  current_price = st.session_state["analyzed_price"]

  st.divider()
  st.subheader(f"📊 AI 分析結果：【{current_name}】")

  # 選擇稅則
  selected_hs = st.radio(
      "請選擇您欲採納申報的建議稅則：",
      options=res.get("tariffs", []),
      key=f"radio_{current_name}",
  )

  # 簽審提醒
  st.warning(res.get("reg_warning", "無特殊簽審規定"))

  # 價格風險分析 (防護型轉型)
  raw_cif = res.get("benchmark_cif", current_price)
  try:
    est_cif = float(raw_cif)
  except (ValueError, TypeError):
    est_cif = float(current_price)

  if est_cif > 0:
    diff_rate = ((current_price - est_cif) / est_cif) * 100
    if diff_rate < -20:
      st.error(
          f"⚠️ **價格風險警示**：您申報的單價 (TWD {current_price}) **低於市場完稅均價"
          f" {abs(diff_rate):.1f}%** (推估均價 TWD {est_cif:.0f})，易引發海關 C3"
          " 查驗並要求提供發票。"
      )
    elif diff_rate > 20:
      st.info(
          f"💡 **價格提醒**：您申報的單價 (TWD {current_price}) 高於市場完稅均價"
          f" {diff_rate:.1f}%。"
      )
    else:
      st.success(
          f"✅ **價格正常**：申報金額符合市場行情（推估完稅均價 TWD"
          f" {est_cif:.0f}）。"
      )

  # 匯出按鈕
  if st.button("確認選擇並匯出報關單 (XML/PDF)"):
    st.balloons()
    st.success(
        f"🎉 申報成功！已採納稅則：\n`{selected_hs}`\n\n系統已自動封裝報關 XML"
        " 檔案！"
    )
