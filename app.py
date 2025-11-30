import solara
import duckdb
import leafmap
import pandas as pd
from ipyleaflet import CircleMarker, Marker  # 引入最底層的繪圖元件

# --- 1. 初始化 DuckDB ---
con = duckdb.connect(database=':memory:')
con.install_extension('spatial')
con.load_extension('spatial')
con.install_extension('httpfs')
con.load_extension('httpfs')

# --- 2. 資料來源 ---
csv_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.csv"

# --- 3. 互動變數 ---
mag_slider = solara.reactive(5.0)  # 為了避免點太多，預設先設 5.0

@solara.component
def Page():
    
    with solara.Column(style={"padding": "20px"}):
        solara.Markdown("# 🌍 地理空間分析儀表板 (暴力繪圖版)")
        solara.Markdown("使用最底層的 **ipyleaflet** 迴圈繪圖，保證點點現形。")

    with solara.Sidebar():
        solara.Markdown("### 📊 篩選條件")
        solara.SliderFloat(label="地震規模", value=mag_slider, min=2.5, max=8.0, step=0.1)

    # --- SQL 查詢 ---
    # 限制只抓前 200 筆，避免手動畫圖太慢
    query = f"""
        SELECT place, mag, time, latitude, longitude
        FROM read_csv_auto('{csv_url}')
        WHERE mag >= {mag_slider.value}
        ORDER BY mag DESC
        LIMIT 200
    """
    
    try:
        df = con.sql(query).df()
        row_count = len(df)
    except Exception as e:
        solara.Error(f"資料讀取失敗: {e}")
        return

    with solara.Column(style={"padding": "0 20px"}):
        solara.Markdown(f"### 查詢結果：顯示前 {row_count} 筆最強地震")
        
        # 1. 建立地圖
        m = leafmap.Map(center=[20, 0], zoom=2)
        
        # --- 測試點：台灣 (確認地圖功能正常) ---
        # 如果你看到這個藍色圖釘，表示地圖功能是好的
        test_marker = Marker(location=[23.5, 121], draggable=False, title="台灣測試點")
        m.add_layer(test_marker)

        # --- 核心修改：暴力迴圈法 ---
        # 不透過 leafmap 的轉換，直接用 Python 迴圈一個一個畫
        if not df.empty:
            for index, row in df.iterrows():
                # 建立一個紅色的圓圈
                circle = CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,           # 半徑
                    color="red",        # 邊框顏色
                    fill_color="red",   # 填充顏色
                    fill_opacity=0.6,   # 透明度
                    weight=1            # 邊框粗細
                )
                # 加到地圖上
                m.add_layer(circle)

        # 顯示地圖
        m.element()

        # 顯示表格
        solara.DataFrame(df)

Page()