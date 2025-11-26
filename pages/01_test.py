# pages/地圖視覺化.py

import solara
import leafmap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. 模擬資料載入函式 (建立一個 GeoDataFrame)
def load_data():
    """模擬載入 NYC 地鐵站資料並建立 GeoDataFrame。"""
    
    # 模擬數據點 (部分真實的 NYC 地鐵站位置)
    data = {
        'Name': ['Times Square', 'Grand Central', 'Union Square', 'Canal Street'],
        'Line': ['A, C, E, N, Q, R, W, 7', '4, 5, 6, 7', '4, 5, 6, L, N, Q, R, W', 'A, C, E, J, N, Q, R, W, Z, 6'],
        'Latitude': [40.758896, 40.752763, 40.734849, 40.718617],
        'Longitude': [-73.985130, -73.979149, -73.991054, -74.000673],
    }
    df = pd.DataFrame(data)
    
    # 將 DataFrame 轉換為 GeoDataFrame
    geometry = gpd.points_from_xy(df.Longitude, df.Latitude)
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    return gdf

# 2. Solara 組件
@solara.component
def Page():
    # 載入資料
    gdf = load_data()
    
    # 使用 solara.use_memo 確保 Leafmap 實例只在必要時重新建立
    map_instance = solara.use_memo(lambda: leafmap.Map(center=(40.74, -74), zoom=12), [])
    
    # 修正錯誤的核心邏輯
    def add_data_layer(m):
        """添加修正後的 GeoDataFrame 層。"""
        
        # ***** 錯誤修正 START *****
        # 修正方法：定義單一樣式字典，避免 Leafmap 誤判為需要主題繪圖 (Thematic Mapping) 的 'column' 參數。
        style = {
            'color': '#FFFFFF',          # 邊框顏色 (stroke_color)
            'weight': 1,                 # 邊框粗細
            'opacity': 1,
            'fillColor': '#FFD700',      # 填充顏色 (fill_color: 黃色)
            'fillOpacity': 0.8,          # 填充透明度
            'radius': 6,                 # 點的半徑
        }
        
        # 呼叫 add_data，傳入 style 字典
        m.add_data(
            gdf,
            layer_type="circle",
            style=style,           # <--- 修正後的關鍵參數
            name="NYC Subway Stations (Fixed)"
        )
        # ***** 錯誤修正 END *****

    # 執行地圖操作
    solara.use_effect(add_data_layer, [map_instance, gdf])

    # 顯示地圖
    return solara.VBox(
        children=[
            solara.Markdown("# 🚇 地圖視覺化頁面 (錯誤已修正)"),
            solara.Markdown(
                "### ℹ️ 修正說明\n\n"
                "您遇到的 `Map.add_data() missing 1 required positional argument: 'column'` 錯誤，"
                "是因為 Leafmap 在特定情況下（如 `layer_type='circle'`）會預期進行**主題繪圖**，"
                "因此強制要求您提供一個數據欄位 (`column`) 來決定點的顏色或大小。\n\n"
                "**修正方法：** 我們現在將所有樣式（`fill_color`, `radius`, `stroke_color` 等）"
                "包裝成一個單一的 `style` 字典，並傳遞給 `m.add_data(..., style=style)`，"
                "這明確告訴 Leafmap 這是**單一樣式繪製**，從而解決了缺少 `column` 參數的問題。"
            ),
            solara.Figure(
                map_instance,
                style={"width": "100%", "height": "600px"}
            )
        ]
    )