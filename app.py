import solara
import duckdb
import leafmap
import pandas as pd
import geopandas as gpd  # 引入地理資料處理神器

# --- 1. 初始化 DuckDB ---
# 使用 :memory: 模式，並載入必要的擴充套件
con = duckdb.connect(database=':memory:')
con.install_extension('spatial')
con.load_extension('spatial')
con.install_extension('httpfs')  # 讓我們可以讀取網路 CSV
con.load_extension('httpfs')

# --- 2. 設定資料來源 ---
# 這裡用 USGS 地震資料做示範
# 之後你可以把這個網址換成你 GitHub 上的馬太鞍溪 CSV 檔 (記得用 Raw 連結)
csv_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.csv"

# --- 3. 建立互動變數 (Reactive State) ---
# 這是讓網頁可以跟使用者互動的關鍵
mag_slider = solara.reactive(4.5)  # 預設篩選規模 4.5 以上

@solara.component
def Page():
    
    # --- 版面配置：標題 ---
    with solara.Column(style={"padding": "20px"}):
        solara.Markdown("# 🌍 地理空間分析儀表板 (DuckDB + Leafmap + GeoPandas)")
        solara.Markdown("結合 **DuckDB** 的極速運算與 **GeoPandas** 的標準化繪圖。")

    # --- 版面配置：側邊欄 ---
    with solara.Sidebar():
        solara.Markdown("### 📊 篩選條件")
        solara.SliderFloat(
            label="最小地震規模 (Magnitude)", 
            value=mag_slider, 
            min=2.5, 
            max=8.0, 
            step=0.1
        )
        solara.Info("調整滑桿後，系統會透過 DuckDB 重新撈取資料。")

    # --- 核心邏輯：資料查詢 ---
    # 使用 f-string 動態組合 SQL 語句
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
        LIMIT 1000
    """
    
    # 執行 SQL 並轉成 DataFrame
    try:
        df = con.sql(query).df()
        row_count = len(df)
    except Exception as e:
        solara.Error(f"資料讀取失敗: {e}")
        return

    # --- 版面配置：主要內容區 ---
    with solara.Column(style={"padding": "0 20px"}):
        solara.Markdown(f"### 🔍 查詢結果：共找到 {row_count} 筆資料")
        
        # 1. 建立地圖物件
        # center=[緯度, 經度], zoom=縮放層級
        m = leafmap.Map(center=[20, 0], zoom=2)
        
        # 2. 如果有資料，進行繪圖
        if not df.empty:
            # --- 關鍵修正：使用 GeoPandas ---
            # 將普通的 DataFrame 轉成 GeoDataFrame
            # 這一步會把經緯度變成真正的「點 (Point)」幾何圖形
            gdf = gpd.GeoDataFrame(
                df, 
                geometry=gpd.points_from_xy(df.longitude, df.latitude)
            )
            
            # 將 GeoDataFrame 加入地圖
            # layer_name: 圖層名稱 (會顯示在地圖右上角的圖層控制裡)
            m.add_gdf(gdf, layer_name="Earthquakes")

        # 3. 渲染地圖
        # 使用 .element() 是 Solara 顯示 Leafmap 的標準方式
        m.element()

        # 4. 顯示數據表格
        solara.Markdown("### 📋 詳細資料表")
        solara.DataFrame(df)

# 啟動應用程式
Page()