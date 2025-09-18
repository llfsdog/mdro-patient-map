#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDRO患者数据处理器
从Excel文件中提取患者数据并转换为GeoJSON格式
"""

import pandas as pd
import json
import os
from typing import Dict, List, Any

def read_excel_data(file_path: str) -> pd.DataFrame:
    """
    读取Excel文件中的MDRO患者数据
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        包含患者数据的DataFrame
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"成功读取Excel文件，共{len(df)}行数据")
        print(f"列名: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    验证经纬度坐标是否有效
    
    Args:
        lat: 纬度
        lon: 经度
        
    Returns:
        坐标是否有效
    """
    # 珠海市大致范围：纬度21.8-22.5，经度113.0-114.0
    # 但考虑到数据可能包含周边地区，适当放宽范围
    return (20.0 <= lat <= 25.0) and (110.0 <= lon <= 120.0)

def validate_strain_type(strain: str) -> bool:
    """
    验证菌种类型是否有效
    
    Args:
        strain: 菌种类型
        
    Returns:
        菌种类型是否有效
    """
    valid_strains = ['MRSA', 'ESBLE', 'CRO', 'OTHER']
    return str(strain).strip().upper() in valid_strains

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗和验证数据
    
    Args:
        df: 原始数据DataFrame
        
    Returns:
        清洗后的DataFrame
    """
    print("开始数据清洗...")
    
    # 删除空行
    df = df.dropna()
    print(f"删除空行后剩余{len(df)}行数据")
    
    # 假设列名可能的变化，尝试自动识别
    # 常见的列名变体
    possible_id_cols = ['患者ID', 'ID', 'id', 'patient_id', 'Patient_ID']
    possible_lat_cols = ['纬度', 'lat', 'latitude', 'Latitude', 'LAT', 'lat_84']
    possible_lon_cols = ['经度', 'lon', 'longitude', 'Longitude', 'LON', 'lng', 'lon_84']
    possible_strain_cols = ['菌种', 'strain', 'Strain', '菌种类型', 'type', 'MRSA', 'ESBLE', 'CRO']
    
    # 自动识别列名
    id_col = None
    lat_col = None
    lon_col = None
    strain_cols = []
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if any(possible in col_lower for possible in ['id', '患者']):
            id_col = col
        elif any(possible in col_lower for possible in ['lat', '纬度']):
            lat_col = col
        elif any(possible in col_lower for possible in ['lon', 'lng', '经度']):
            lon_col = col
        elif any(possible in col_lower for possible in ['strain', '菌种', 'mrsa', 'esble', 'cro']):
            strain_cols.append(col)
    
    print(f"识别的列名 - ID: {id_col}, 纬度: {lat_col}, 经度: {lon_col}, 菌种列: {strain_cols}")
    
    if not all([id_col, lat_col, lon_col]) or len(strain_cols) == 0:
        print("无法自动识别所有必需的列，请检查Excel文件格式")
        print("需要的列：患者ID、纬度、经度、至少一个菌种列")
        return None
    
    # 重命名列
    df = df.rename(columns={
        id_col: 'patient_id',
        lat_col: 'latitude',
        lon_col: 'longitude'
    })
    
    # 数据类型转换
    try:
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # 处理菌种列 - 将布尔值或数值转换为菌种名称
        for strain_col in strain_cols:
            # 将非零值转换为菌种名称
            df[strain_col] = df[strain_col].apply(
                lambda x: strain_col.upper() if pd.notna(x) and x != 0 and x != '0' and str(x).lower() not in ['false', 'no', ''] else None
            )
        
        # 创建菌种列 - 取第一个非空的菌种
        df['strain'] = None
        for strain_col in strain_cols:
            mask = df['strain'].isna() & df[strain_col].notna()
            df.loc[mask, 'strain'] = df.loc[mask, strain_col]
        
        # 将没有菌种信息的患者标记为"OTHER"
        df['strain'] = df['strain'].fillna('OTHER')
        
        # 不再删除没有菌种信息的行，而是标记为OTHER
        
    except Exception as e:
        print(f"数据类型转换失败: {e}")
        return None
    
    # 删除转换失败的行
    original_count = len(df)
    df = df.dropna(subset=['latitude', 'longitude'])
    print(f"删除无效坐标后剩余{len(df)}行数据")
    
    # 验证坐标范围
    valid_coords = df.apply(
        lambda row: validate_coordinates(row['latitude'], row['longitude']), 
        axis=1
    )
    df = df[valid_coords]
    print(f"验证坐标范围后剩余{len(df)}行数据")
    
    # 验证菌种类型
    valid_strains = df['strain'].apply(validate_strain_type)
    df = df[valid_strains]
    print(f"验证菌种类型后剩余{len(df)}行数据")
    
    # 删除重复数据
    df = df.drop_duplicates(subset=['patient_id'])
    print(f"删除重复数据后剩余{len(df)}行数据")
    
    print(f"数据清洗完成，最终有效数据{len(df)}条")
    return df

def create_geojson(df: pd.DataFrame) -> Dict[str, Any]:
    """
    将DataFrame转换为GeoJSON格式
    
    Args:
        df: 清洗后的数据DataFrame
        
    Returns:
        GeoJSON格式的数据
    """
    features = []
    
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "properties": {
                "id": str(row['patient_id']),
                "strain": row['strain']
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['longitude']), float(row['latitude'])]
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return geojson

def generate_heatmap_data(df: pd.DataFrame) -> List[List[float]]:
    """
    生成热力图数据
    
    Args:
        df: 清洗后的数据DataFrame
        
    Returns:
        热力图数据点列表
    """
    heatmap_points = []
    
    for _, row in df.iterrows():
        # 热力图数据格式：[纬度, 经度, 强度]
        # 这里使用固定强度1.0，实际应用中可以根据其他因素调整
        point = [float(row['latitude']), float(row['longitude']), 1.0]
        heatmap_points.append(point)
    
    return heatmap_points

def process_mdro_data(excel_file: str, output_dir: str = "data") -> bool:
    """
    处理MDRO数据的完整流程
    
    Args:
        excel_file: Excel文件路径
        output_dir: 输出目录
        
    Returns:
        处理是否成功
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 读取Excel数据
        df = read_excel_data(excel_file)
        if df is None:
            return False
        
        # 清洗数据
        df_clean = clean_data(df)
        if df_clean is None or len(df_clean) == 0:
            print("数据清洗失败或无有效数据")
            return False
        
        # 生成GeoJSON
        geojson_data = create_geojson(df_clean)
        
        # 生成热力图数据
        heatmap_data = generate_heatmap_data(df_clean)
        
        # 保存GeoJSON文件
        geojson_file = os.path.join(output_dir, "mdro_patients.json")
        with open(geojson_file, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, ensure_ascii=False, indent=2)
        print(f"GeoJSON数据已保存到: {geojson_file}")
        
        # 保存热力图数据
        heatmap_file = os.path.join(output_dir, "heatmap_data.json")
        with open(heatmap_file, 'w', encoding='utf-8') as f:
            json.dump(heatmap_data, f, ensure_ascii=False, indent=2)
        print(f"热力图数据已保存到: {heatmap_file}")
        
        # 生成统计信息
        stats = {
            "total_patients": len(df_clean),
            "strain_distribution": df_clean['strain'].value_counts().to_dict(),
            "coordinate_bounds": {
                "min_lat": float(df_clean['latitude'].min()),
                "max_lat": float(df_clean['latitude'].max()),
                "min_lon": float(df_clean['longitude'].min()),
                "max_lon": float(df_clean['longitude'].max())
            }
        }
        
        stats_file = os.path.join(output_dir, "data_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"统计信息已保存到: {stats_file}")
        
        print("\n=== 数据处理完成 ===")
        print(f"总患者数: {stats['total_patients']}")
        print("菌种分布:")
        for strain, count in stats['strain_distribution'].items():
            print(f"  {strain}: {count}例")
        print(f"坐标范围: 纬度 {stats['coordinate_bounds']['min_lat']:.4f} - {stats['coordinate_bounds']['max_lat']:.4f}")
        print(f"        经度 {stats['coordinate_bounds']['min_lon']:.4f} - {stats['coordinate_bounds']['max_lon']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"数据处理过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 处理MDRO数据
    excel_file = "副本MDRO.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Excel文件 {excel_file} 不存在")
        print("请确保副本MDRO.xlsx文件在当前目录下")
    else:
        success = process_mdro_data(excel_file)
        if success:
            print("\n✅ 数据处理成功！可以开始创建地图应用了。")
        else:
            print("\n❌ 数据处理失败，请检查Excel文件格式。")
