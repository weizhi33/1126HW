import solara
import duckdb
import leafmap.foliumap as leafmap  # <--- 關鍵修改：改用 Folium 引擎 (靜態渲染)
import pandas as pd

# --- 1. 初始化 DuckDB ---
con = duckdb.connect(database=':memory:')
con.install_extension('spatial')
con.load_extension('spatial')
con.install_extension('httpfs')
con.load_extension('httpfs')

# --- 2. 資料來源 ---
csv_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.csv"

# --- 3. 互動變數 ---
mag_slider = solara.reactive(5.0)

@solara.component
def Page():
    
    with solara.Column(style={"padding": "20px"}):
        solara.Markdown("# 🌍 地理空間分析儀表板 (Folium iframe 版)")
        solara.Markdown("使用 **iframe** 強制渲染，解決 Docker 環境下通訊失敗的問題。")

    with solara.Sidebar():
        solara.Markdown("### 📊 篩選條件")
        solara.SliderFloat(label="地震規模", value=mag_slider, min=2.5, max=8.0, step=0.1)

    # --- SQL 查詢 ---
    query = f"""
        SELECT place, mag, time, latitude, longitude
        FROM read_csv_auto('{csv_url}')
        WHERE mag >= {mag_slider.value}
        ORDER BY mag DESC
        LIMIT 300
    """
    
    try:
        df = con.sql(query).df()
        row_count = len(df)
    except Exception as e:
        solara.Error(f"資料讀取失敗: {e}")
        return

    with solara.Column(style={"padding": "0 20px"}):
        solara.Markdown(f"### 查詢結果：顯示前 {row_count} 筆資料")
        
        # 1. 建立地圖 (使用 Folium 引擎)
        m = leafmap.Map(center=[20, 0], zoom=2)
        
        # 2. 加入資料點
        if not df.empty:
            # Folium 引擎的語法跟原本很像，但它是生成靜態 HTML
            m.add_points_from_xy(
                df, 
                x="longitude", 
                y="latitude",
                popup=["place", "mag", "time"]
            )
        
        # 3. 🔥 關鍵修改：使用 iframe 顯示 🔥
        # 我們把地圖轉成一段 HTML 文字，直接塞進 iframe 裡
        # 這樣就繞過了任何 websocket 通訊問題
        map_html = m.to_html()
        
        # 使用 Solara 的 HTML 元件來渲染 iframe
        solara.HTML(
            tag="iframe", 
            attributes={
                "srcdoc": map_html,  # 把地圖 HTML 直接塞進去
                "width": "100%", 
                "height": "600px", 
                "style": "border: none;"
            }
        )

        # 顯示表格
        solara.DataFrame(df)

Page()