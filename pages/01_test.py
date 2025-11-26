import solara
import leafmap.maplibregl as leafmap # Solara 經常與 Leafmap 的 maplibregl 後端更好地整合，但 foliumap 也可以
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# 假設的資料載入函式 (您必須根據實際資料替換此處)
def load_data():
    """載入並準備 GeoDataFrame (gdf) 資料。"""
    try:
        # **!!! 請替換成您的實際資料載入邏輯 !!!**
        # 這裡使用簡單的範例數據作為佔位符
        data = {
            'City': ['NYC', 'Newark', 'Jersey City'],
            'Latitude': [40.7128, 40.7357, 40.7178],
            'Longitude': [-74.0060, -74.1724, -74.0431],
            'StationName': ['Station A', 'Station B', 'Station C']
        }
        df = pd.DataFrame(data)
        gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
            crs="EPSG:4326" # 設定坐標系
        )
        return gdf
    except Exception as e:
        print(f"資料載入失敗: {e}")
        return None

# 定義 Solara 頁面元件
@solara.component
def Page():
    solara.Title("Leafmap 地圖視覺化")
    
    # 載入資料
    gdf = load_data()
    if gdf is None:
        solara.Error("無法載入地理數據。請檢查資料來源和格式。")
        return

    # --- 步驟 5: 使用 Leafmap 繪製地圖 ---
    # 老師提供的 Leafmap 程式碼
    
    # 建立地圖實例
    # 使用 Leafmap 的 ipyleaflet 或 foliumap 後端都可以，但 Solara 建議使用 Leafmap 支援的 ipywidgets 後端
    # 這裡我們使用 foliumap (folium) 進行繪製，然後讓 Solara 渲染它
    
    try:
        # 1. 初始化地圖 (使用 foliumap 確保 add_data 相容性)
        m = leafmap.Map(
            style="dark-matter", # 設定底圖樣式
            # 這裡的 center 和 zoom 可以根據您的 NYC 數據中心調整
            center=(40.75, -74.00), 
            zoom=10, 
            height="700px" # 設定高度
        )
        
        # 2. 新增底圖
        m.add_basemap("Esri.WorldImagery")
        
        # 3. 新增資料
        m.add_data(
            gdf,
            layer_type="circle",
            fill_color="#FFD700",
            radius=6,
            stroke_color="#FFFFFF",
            name="NYC Subway Stations"
        )
        
        # 4. 顯示地圖：將 Leafmap 的地圖物件轉換為 Solara 元件
        # 使用 m.to_solara() 即可讓 Solara 渲染 ipywidgets/folium 物件
        solara.Markdown("### 紐約地鐵站點分佈")
        return m.to_solara()
        
    except Exception as e:
        solara.Error(f"地圖渲染錯誤: {e}")

# 備註：在 Solara 中，您不需要像 Streamlit 那樣有 01_02 的命名順序，只要在 pages 資料夾下即可。