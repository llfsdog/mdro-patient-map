# MDRO患者分布地图

一个基于Web的交互式地图应用，用于可视化MDRO（多重耐药菌）患者的分布情况。

## 🌐 在线访问

**直接访问：** [https://llfsdog.github.io/mdro-patient-map/](https://llfsdog.github.io/mdro-patient-map/)

## 📊 功能特性

- **患者聚类显示**：深红色圆圈表示患者聚集区域
- **患者点图**：显示具体患者位置，不同菌种用不同颜色标识
- **热力图**：显示患者密度分布
- **菌种筛选**：支持按ESBLE、MRSA、CRO筛选
- **底图切换**：简洁地图、深色地图、街道地图
- **统计信息**：实时显示患者数量和菌种分布

## 🎨 界面布局

- **左上角**：显示控制面板（图层切换、菌种筛选）
- **右上角**：统计信息面板
- **左下角**：图层控制面板（底图切换）
- **右下角**：图例说明面板

## 📈 数据概览

- **总患者数**：454例
- **菌种分布**：ESBLE(404例) > MRSA(40例) > CRO(10例)
- **地理范围**：广东省及周边地区

## 🚀 本地运行

### 方法1：使用启动脚本（推荐）
```bash
# 双击启动地图.bat文件
启动地图.bat
```

### 方法2：命令行启动
```bash
# 进入项目目录
cd MDRO_Map_App

# 启动HTTP服务器
python -m http.server 8000

# 浏览器访问
http://localhost:8000
```

## 🔧 技术栈

- **前端**：HTML5, CSS3, JavaScript
- **地图库**：Leaflet.js
- **数据处理**：Python + pandas
- **部署**：GitHub Pages

## 📁 项目结构

```
MDRO_Map_App/
├── index.html              # 主地图应用
├── data_processor.py       # 数据处理器
├── data/                   # 数据文件夹
│   ├── mdro_patients.json  # 患者数据
│   ├── heatmap_data.json   # 热力图数据
│   └── data_stats.json     # 统计信息
├── 启动地图.bat            # 启动脚本
└── README.md              # 项目说明
```

## 🔄 更新数据

如需更新患者数据：

1. 将新的Excel文件命名为 `MDRO.xlsx`
2. 运行数据处理脚本：
   ```bash
   python data_processor.py
   ```
3. 提交更改到GitHub：
   ```bash
   git add .
   git commit -m "更新患者数据"
   git push origin main
   ```

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 创建 [Issue](https://github.com/llfsdog/mdro-patient-map/issues)
- 发送邮件至项目维护者

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为MDRO研究做出贡献的医疗工作者和研究人员。

---

**版本**：v1.1.0  
**最后更新**：2024年12月
