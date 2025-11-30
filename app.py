import solara
import duckdb
import leafmap  # <--- 修改這裡：直接 import leafmap 本體
import pandas as pd

# 1. 初始化 DuckDB 並安裝空間擴充套件
# 這裡使用 :memory: 因為在 Hugging Face 上我們通常不需要持久化儲存
con = duckdb.connect(database=':memory:')
con.install_extension('spatial')
con.load_extension('spatial')
con.install_extension('httpfs') # 讓我們可以直接讀取網路上的 CSV
con.load_extension('httpfs')

# 2. 定義資料來源 (您可以換成您 GitHub 上的 Raw CSV 連結)
# 這裡示範用 USGS 的地震資料
csv_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.csv"

# 3. 建立 Reactive 變數 (讓網頁可以互動)
mag_slider = solara.reactive(4.0) # 預設篩選規模 4.0 以上

@solara.component
def Page():
    
    # --- 標題區 ---
    with solara.Column(style={"padding": "20px"}):
        solara.Markdown("# 🌍 地理空間分析儀表板 (DuckDB + Leafmap)")
        solara.Markdown("這個網頁示範如何使用 **DuckDB SQL** 快速過濾網路上的空間資料。")

    # --- 側邊欄控制區 ---
    with solara.Sidebar():
        solara.Markdown("### 📊 篩選條件")
        solara.SliderFloat(label="最小地震規模 (Magnitude)", value=mag_slider, min=2.5, max=8.0, step=0.1)
        
        solara.Info("調整滑桿後，DuckDB 會即時執行 SQL 查詢。")

    # --- 核心邏輯：用 DuckDB SQL 撈資料 ---
    # 組合 SQL 語句
    query = f"""
        SELECT 
            time, 
            place, 
            mag, 
            depth, 
            latitude, 
            longitude
        FROM read_csv_auto('{csv_url}')
        WHERE mag >= {mag_slider.value}
        ORDER BY mag DESC
        LIMIT 500
    """
    
    # 執行查詢並轉成 Pandas DataFrame
    try:
        df = con.sql(query).df()
        row_count = len(df)
    except Exception as e:
        solara.Error(f"資料讀取錯誤: {e}")
        return

# --- 顯示區 ---
    with solara.Column(style={"padding": "0 20px"}):
        solara.Markdown(f"### 🔍 查詢結果：共找到 {row_count} 筆資料")
        
        # 顯示地圖
        m = leafmap.Map(center=[23.5, 121], zoom=4) 
        
        if not df.empty:
            m.add_circle_markers_from_xy(
                df, 
                x="longitude", 
                y="latitude", 
                radius=10, 
                color="red", 
                fill_color="orange",
                popup=["place", "mag", "time"] 
            )
        
        # 🔥 關鍵修改：用 .element() 讓 Solara 顯示地圖 🔥
        m.element()

        # 顯示資料表 (表格)
        solara.Markdown("### 📋 詳細資料表")
        solara.DataFrame(df)

# 這行是給 Solara 執行的入口
Page()