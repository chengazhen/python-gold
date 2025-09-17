# 黄金数据获取工具

这是一个优化后的黄金价格数据获取和分析工具，支持多种类型的黄金数据分类管理。

## 项目特点

### 🔥 主要优化
- **分类明确**: 通过文件名清晰区分不同类型的黄金数据
- **类型支持**: 支持首饰黄金、实物黄金、金条三种类型
- **配置化**: 每种黄金类型都有独立的配置参数
- **文件管理**: 自动生成规范的文件名，支持时间戳版本
- **数据管理器**: 提供统一的数据管理接口

### 📁 文件命名规则
```
首饰黄金: jewelry_gold_latest.json, jewelry_gold_20250917_143022.json
实物黄金: physical_gold_latest.json, physical_gold_20250917_143022.json
金条数据: gold_bar_latest.json, gold_bar_20250917_143022.json
```

## 项目结构

```
gold/
├── xinlang.py              # 核心数据获取和解析模块 (已优化)
├── gold_data_manager.py    # 数据管理器 (新增)
├── example_usage.py        # 使用示例 (新增)
├── README.md              # 项目说明 (新增)
└── 数据文件/
    ├── jewelry_gold_latest.json      # 首饰黄金最新数据
    ├── jewelry_gold_analysis.json    # 首饰黄金分析结果
    ├── physical_gold_latest.json     # 实物黄金最新数据
    ├── gold_bar_latest.json          # 金条最新数据
    └── ...时间戳版本文件
```

## 黄金类型配置

### 1. 首饰黄金 (jewelry)
- **参数**: `pp=0, pz=15`
- **描述**: 各大品牌首饰黄金价格数据
- **文件前缀**: `jewelry_gold`

### 2. 实物黄金 (physical)
- **参数**: `pp=1, pz=20`
- **描述**: 实物黄金投资产品价格数据
- **文件前缀**: `physical_gold`

### 3. 金条 (gold_bar)
- **参数**: `pp=2, pz=25`
- **描述**: 各种规格金条价格数据
- **文件前缀**: `gold_bar`

## 使用方法

### 方法1: 直接运行主程序
```bash
python xinlang.py
```
程序会提示选择黄金类型和数据源，然后自动获取、解析、分析和保存数据。

### 方法2: 使用数据管理器
```python
from gold_data_manager import GoldDataManager
from xinlang import GoldType

# 创建数据管理器
manager = GoldDataManager()

# 获取首饰黄金数据
manager.fetch_and_save_data(GoldType.JEWELRY)

# 获取所有类型数据汇总
summary = manager.get_all_data_summary()
print(summary)

# 导出合并数据到Excel
manager.export_combined_data()
```

### 方法3: 直接调用函数
```python
from xinlang import GoldType, fetch_gold_data_from_sina, parse_complete_gold_data, save_data

# 获取实物黄金数据
html_text = fetch_gold_data_from_sina(GoldType.PHYSICAL)
gold_data = parse_complete_gold_data(html_text, GoldType.PHYSICAL)
save_data(gold_data, analysis, GoldType.PHYSICAL)
```

## 自定义参数

可以通过URL参数获取特定的数据：

```python
# 自定义参数示例
custom_params = {
    "pp": 0,              # 品牌参数
    "pz": 20,             # 品种参数
    "start": "2025-08-01", # 开始日期
    "end": "2025-09-17"    # 结束日期
}

html_text = fetch_gold_data_from_sina(
    gold_type=GoldType.JEWELRY,
    custom_params=custom_params
)
```

## 数据格式

每条黄金数据包含以下字段：
```json
{
    "日期": "2025-09-17",
    "品牌": "周大福",
    "产品": "足金饰品",
    "价格": "588.00",
    "价格_数值": 588.0,
    "单位": "元/克",
    "纯度": "足金999",
    "手工费": "50",
    "涨跌": "↑",
    "黄金类型": "首饰黄金",
    "黄金类型代码": "jewelry",
    "数据来源": "新浪财经",
    "解析时间": "2025-09-17T14:30:22"
}
```

## 功能特性

### 🎯 数据获取
- 支持从新浪财经自动获取数据
- 支持自定义URL参数
- 支持从本地HTML文件读取
- 自动处理编码问题

### 📊 数据分析
- 品牌统计和排名
- 产品类型分析
- 价格统计 (最高价、最低价、平均价、中位数)
- 涨跌趋势分析
- 日期分布统计

### 💾 数据存储
- JSON格式 (最新版本 + 时间戳版本)
- Excel格式 (需要pandas)
- 自动生成规范文件名
- 支持中文内容正确显示

### 🔧 数据管理
- 统一的数据管理接口
- 跨类型数据比较
- 数据汇总和统计
- 合并导出功能

## 运行示例

查看 `example_usage.py` 文件了解详细的使用示例：

```bash
python example_usage.py
```

## 依赖包

```bash
pip install requests pandas openpyxl
```

## 扩展说明

### 添加新的黄金类型
1. 在 `GoldType` 枚举中添加新类型
2. 在 `GoldDataConfig.GOLD_CONFIGS` 中添加配置
3. 根据需要调整URL参数

### 自定义数据源
可以通过 `custom_url` 参数使用其他数据源：
```python
html_text = fetch_gold_data_from_sina(
    gold_type=GoldType.JEWELRY,
    custom_url="https://your-custom-url.com/gold-data"
)
```

## 注意事项

1. **网络连接**: 需要稳定的网络连接访问新浪财经
2. **编码处理**: 程序会自动尝试多种编码方式
3. **数据更新**: 建议定期运行以获取最新数据
4. **文件管理**: 程序会自动创建时间戳版本，避免数据覆盖

## 更新日志

### v2.0 (当前版本)
- ✅ 添加黄金类型分类支持
- ✅ 优化文件命名规则
- ✅ 新增数据管理器
- ✅ 添加使用示例
- ✅ 改进配置管理
- ✅ 支持自定义参数

### v1.0 (原版本)
- ✅ 基本数据获取功能
- ✅ 数据解析和分析
- ✅ JSON和Excel导出
