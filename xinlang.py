import re
import json
import pandas as pd
import requests
from datetime import datetime
from collections import Counter
from enum import Enum
from pathlib import Path


class GoldType(Enum):
    """黄金类型枚举"""

    JEWELRY = "jewelry"  # 首饰黄金
    PHYSICAL = "physical"  # 实物黄金
    GOLD_BAR = "gold_bar"  # 金条


class GoldDataConfig:
    """黄金数据配置类"""

    # 不同类型黄金的URL参数配置
    GOLD_CONFIGS = {
        GoldType.JEWELRY: {
            "name": "首饰黄金",
            "filename_prefix": "jewelry_gold",
            "url_params": {"pp": 0, "pz": 15},  # 首饰黄金参数
            "description": "各大品牌首饰黄金价格数据",
        },
        GoldType.PHYSICAL: {
            "name": "实物黄金",
            "filename_prefix": "physical_gold",
            "url_params": {"pp": 0, "pz": 11},  # 实物黄金参数（示例）
            "description": "实物黄金投资产品价格数据",
        },
        GoldType.GOLD_BAR: {
            "name": "金条",
            "filename_prefix": "gold_bar",
            "url_params": {"pp": 0, "pz": 15},  # 金条参数（示例）
            "description": "各种规格金条价格数据",
        },
    }

    BASE_URL = "https://vip.stock.finance.sina.com.cn/q/view/vGold_Matter_History.php"

    @classmethod
    def get_config(cls, gold_type: GoldType):
        """获取指定黄金类型的配置"""
        return cls.GOLD_CONFIGS.get(gold_type, cls.GOLD_CONFIGS[GoldType.JEWELRY])

    @classmethod
    def get_filename(
        cls, gold_type: GoldType, file_type: str = "json", timestamp: bool = True
    ):
        """生成文件名"""
        config = cls.get_config(gold_type)
        prefix = config["filename_prefix"]

        if timestamp:
            time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{prefix}_{time_str}.{file_type}"
        else:
            return f"{prefix}_latest.{file_type}"


def fetch_gold_data_from_sina(
    gold_type: GoldType = GoldType.JEWELRY,
    custom_url: str = None,
    custom_params: dict = None,
):
    """从新浪财经获取黄金数据"""
    # 获取配置
    config = GoldDataConfig.get_config(gold_type)

    # 构建URL和参数
    if custom_url:
        url = custom_url
    else:
        url = GoldDataConfig.BASE_URL

    if custom_params:
        params = custom_params
    else:
        params = config["url_params"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        print(f"正在获取{config['name']}数据: {url}")
        print(f"请求参数: {params}")

        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # 尝试不同的编码方式，优先使用GBK（新浪财经使用GBK编码）
        encodings = ["gbk", "gb2312", "utf-8", "big5"]
        html_content = None

        for encoding in encodings:
            try:
                response.encoding = encoding
                html_content = response.text
                # 检查是否包含中文字符
                if (
                    "黄金" in html_content
                    or "价格" in html_content
                    or "品牌" in html_content
                ):
                    print(f"成功使用 {encoding} 编码解析网页，检测到中文内容")
                    break
                else:
                    print(f"使用 {encoding} 编码但未检测到中文内容，尝试下一个编码")
            except Exception as e:
                print(f"使用 {encoding} 编码失败: {e}")
                continue

        if html_content is None:
            print("无法解析网页编码，使用默认编码")
            html_content = response.text

        print(f"网页内容长度: {len(html_content)} 字符")
        return html_content

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None
    except Exception as e:
        print(f"获取网页数据时发生错误: {e}")
        return None


def fetch_gold_data_from_web(url=None, params=None):
    """从网页获取黄金数据"""
    if url is None:
        url = "https://vip.stock.finance.sina.com.cn/q/view/vGold_Matter_History.php"

    if params is None:
        params = {
            "pp": 0,  # 品牌参数
            "pz": 15,  # 品种参数
            "start": "2025-08-17",  # 开始日期
            "end": "2025-09-17",  # 结束日期
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        print(f"正在从网页获取数据: {url}")
        print(f"请求参数: {params}")

        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # 尝试不同的编码方式，优先使用GBK（新浪财经使用GBK编码）
        encodings = ["gbk", "gb2312", "utf-8", "big5"]
        html_content = None

        for encoding in encodings:
            try:
                response.encoding = encoding
                html_content = response.text
                # 检查是否包含中文字符
                if (
                    "黄金" in html_content
                    or "价格" in html_content
                    or "品牌" in html_content
                ):
                    print(f"成功使用 {encoding} 编码解析网页，检测到中文内容")
                    break
                else:
                    print(f"使用 {encoding} 编码但未检测到中文内容，尝试下一个编码")
            except Exception as e:
                print(f"使用 {encoding} 编码失败: {e}")
                continue

        if html_content is None:
            print("无法解析网页编码，使用默认编码")
            html_content = response.text

        print(f"网页内容长度: {len(html_content)} 字符")
        return html_content

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None
    except Exception as e:
        print(f"获取网页数据时发生错误: {e}")
        return None


def parse_complete_gold_data(html_text, gold_type: GoldType = GoldType.JEWELRY):
    """解析完整的黄金数据"""
    config = GoldDataConfig.get_config(gold_type)

    # 匹配表格行的正则表达式 - 针对新浪财经网页格式
    # 匹配格式：<td>日期</td><td>品牌</td><td>产品</td><td>价格</td><td>单位</td><td>纯度</td><td>手工费</td><td>涨跌</td>
    pattern = r"<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>"

    # 也匹配带div的格式
    pattern2 = r"<td[^>]*><div[^>]*>([^<]*)</div></td>\s*<td[^>]*><div[^>]*>([^<]*)</div></td>\s*<td[^>]*><div[^>]*>([^<]*)</div></td>\s*<td[^>]*><div[^>]*>([^<]*)</div></td>\s*<td[^>]*><div[^>]*>([^<]*)</div></td>\s*<td[^>]*><div[^>]*>([^<]*)</div></td>\s*<td[^>]*><div[^>]*>([^<]*)</div></td>\s*<td[^>]*><div[^>]*>([^<]*)</div></td>"

    matches1 = re.findall(pattern, html_text, re.DOTALL)
    matches2 = re.findall(pattern2, html_text, re.DOTALL)

    # 合并匹配结果并去重
    all_matches = []
    seen = set()

    for match in matches1 + matches2:
        if len(match) >= 7:
            # 使用前几个字段作为唯一标识
            key = (match[0], match[1], match[2], match[3])
            if key not in seen:
                seen.add(key)
                all_matches.append(match)

    gold_data = []

    for match in all_matches:
        if len(match) >= 7:
            date, brand, product, price, unit, purity, craft_fee, trend = match[:8]

            # 清理数据
            date = date.strip()
            brand = brand.strip()
            product = product.strip()
            price = price.strip()
            unit = unit.strip()
            purity = purity.strip()
            craft_fee = craft_fee.strip()
            trend = trend.strip()

            # 验证数据有效性
            if date and brand and product and price and unit:
                # 提取价格数值
                price_match = re.search(r"(\d+\.?\d*)", price)
                price_value = float(price_match.group(1)) if price_match else None

                data = {
                    "日期": date,
                    "品牌": brand,
                    "产品": product,
                    "价格": price,
                    "价格_数值": price_value,
                    "单位": unit,
                    "纯度": purity,
                    "手工费": craft_fee,
                    "涨跌": trend,
                    "黄金类型": config["name"],
                    "黄金类型代码": gold_type.value,
                    "数据来源": "新浪财经",
                    "解析时间": datetime.now().isoformat(),
                }
                gold_data.append(data)

    return gold_data


def analyze_gold_data(gold_data):
    """分析黄金数据"""
    if not gold_data:
        return {}

    # 基本统计
    total_records = len(gold_data)

    # 品牌统计
    brands = [item["品牌"] for item in gold_data]
    brand_counts = Counter(brands)

    # 产品统计
    products = [item["产品"] for item in gold_data]
    product_counts = Counter(products)

    # 价格分析
    prices = [item["价格_数值"] for item in gold_data if item["价格_数值"] is not None]
    price_analysis = {}
    if prices:
        price_analysis = {
            "最高价": max(prices),
            "最低价": min(prices),
            "平均价": sum(prices) / len(prices),
            "中位数": sorted(prices)[len(prices) // 2],
            "记录数": len(prices),
        }

    # 趋势统计
    trends = [item["涨跌"] for item in gold_data]
    trend_counts = Counter(trends)

    # 日期统计
    dates = [item["日期"] for item in gold_data]
    date_counts = Counter(dates)

    return {
        "数据概览": {
            "总记录数": total_records,
            "数据日期范围": f"{min(dates)} 至 {max(dates)}" if dates else "无数据",
            "品牌数量": len(brand_counts),
            "产品类型数量": len(product_counts),
            "有效价格记录数": len(prices),
        },
        "品牌分析": {
            "品牌统计": dict(brand_counts.most_common()),
            "主要品牌": dict(brand_counts.most_common(10)),
        },
        "产品分析": {
            "产品类型统计": dict(product_counts.most_common()),
            "热门产品": dict(product_counts.most_common(10)),
        },
        "价格分析": price_analysis,
        "趋势分析": {
            "涨跌统计": dict(trend_counts),
            "涨跌比例": {
                k: f"{(v/total_records*100):.1f}%" for k, v in trend_counts.items()
            },
        },
        "日期分析": {
            "日期统计": dict(date_counts.most_common()),
            "数据日期数": len(date_counts),
        },
    }


def print_analysis_report(analysis):
    """打印分析报告"""
    print("=" * 60)
    print("黄金数据解析分析报告")
    print("=" * 60)

    # 数据概览
    overview = analysis["数据概览"]
    print(f"📊 数据概览:")
    print(f"   总记录数: {overview['总记录数']}")
    print(f"   数据日期范围: {overview['数据日期范围']}")
    print(f"   品牌数量: {overview['品牌数量']}")
    print(f"   产品类型数量: {overview['产品类型数量']}")
    print(f"   有效价格记录数: {overview['有效价格记录数']}")

    # 品牌分析
    print(f"\n🏷️ 主要品牌 (前10名):")
    for i, (brand, count) in enumerate(analysis["品牌分析"]["主要品牌"].items(), 1):
        print(f"   {i:2d}. {brand}: {count}条记录")

    # 产品分析
    print(f"\n📦 热门产品 (前10名):")
    for i, (product, count) in enumerate(analysis["产品分析"]["热门产品"].items(), 1):
        print(f"   {i:2d}. {product}: {count}条记录")

    # 价格分析
    if analysis["价格分析"]:
        price_info = analysis["价格分析"]
        print(f"\n💰 价格分析:")
        print(f"   最高价: {price_info['最高价']:.2f}元/克")
        print(f"   最低价: {price_info['最低价']:.2f}元/克")
        print(f"   平均价: {price_info['平均价']:.2f}元/克")
        print(f"   中位数: {price_info['中位数']:.2f}元/克")
        print(f"   有效价格记录数: {price_info['记录数']}")

    # 趋势分析
    print(f"\n📈 涨跌情况:")
    for trend, ratio in analysis["趋势分析"]["涨跌比例"].items():
        print(f"   {trend}: {ratio}")

    # 日期分析
    print(f"\n📅 数据日期分布:")
    print(f"   数据日期数: {analysis['日期分析']['数据日期数']}")
    for date, count in list(analysis["日期分析"]["日期统计"].items())[:5]:
        print(f"   {date}: {count}条记录")


def save_data(gold_data, analysis, gold_type: GoldType = GoldType.JEWELRY):
    """保存数据到文件"""

    # 生成文件名
    json_filename = GoldDataConfig.get_filename(gold_type, "json", timestamp=False)
    analysis_filename = GoldDataConfig.get_filename(
        gold_type, "json", timestamp=False
    ).replace(".json", "_analysis.json")
    excel_filename = GoldDataConfig.get_filename(gold_type, "xlsx", timestamp=False)

    # 同时保存带时间戳的版本
    json_filename_ts = GoldDataConfig.get_filename(gold_type, "json", timestamp=True)
    analysis_filename_ts = GoldDataConfig.get_filename(
        gold_type, "json", timestamp=True
    ).replace(".json", "_analysis.json")

    # 保存原始数据到JSON，确保中文正确显示
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(gold_data, f, ensure_ascii=False, indent=2)

    with open(json_filename_ts, "w", encoding="utf-8") as f:
        json.dump(gold_data, f, ensure_ascii=False, indent=2)

    # 保存分析结果到JSON，确保中文正确显示
    with open(analysis_filename, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    with open(analysis_filename_ts, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # 如果有pandas，保存到Excel
    try:
        df = pd.DataFrame(gold_data)
        df.to_excel(excel_filename, index=False)
        print(f"\n💾 数据已保存:")
        print(f"   - JSON数据: {json_filename}")
        print(f"   - 分析结果: {analysis_filename}")
        print(f"   - Excel文件: {excel_filename}")
        print(f"   - 带时间戳版本: {json_filename_ts}, {analysis_filename_ts}")
    except ImportError:
        print(f"\n💾 数据已保存:")
        print(f"   - JSON数据: {json_filename}")
        print(f"   - 分析结果: {analysis_filename}")
        print(f"   - 带时间戳版本: {json_filename_ts}, {analysis_filename_ts}")
        print(f"   - 注意: 需要安装pandas才能保存Excel文件")


def main():
    """主函数 - 自动获取所有类型黄金数据"""
    print("黄金数据解析工具")
    print("=" * 40)
    print("🔄 正在从新浪财经获取所有类型黄金数据...")
    print("=" * 40)

    # 定义所有黄金类型
    all_gold_types = [GoldType.JEWELRY, GoldType.PHYSICAL, GoldType.GOLD_BAR]

    # 存储所有数据
    all_data = []
    all_analysis = {}

    # 逐个获取每种类型的数据
    for gold_type in all_gold_types:
        config = GoldDataConfig.get_config(gold_type)
        print(f"\n📊 正在获取{config['name']}数据...")

        # 从新浪财经获取数据
        html_text = fetch_gold_data_from_sina(gold_type)

        if html_text:
            print(f"✅ 成功从新浪财经获取{config['name']}数据")

            # 保存HTML文件
            html_filename = GoldDataConfig.get_filename(
                gold_type, "html", timestamp=False
            )
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html_text)
            print(f"📁 网页数据已保存到 {html_filename}")

            # 解析数据
            print(f"正在解析{config['name']}数据...")
            gold_data = parse_complete_gold_data(html_text, gold_type)

            if gold_data:
                print(f"✅ 成功解析 {len(gold_data)} 条{config['name']}数据")

                # 分析数据
                print("正在分析数据...")
                analysis = analyze_gold_data(gold_data)

                # 保存数据
                save_data(gold_data, analysis, gold_type)

                # 添加到汇总数据
                all_data.extend(gold_data)
                all_analysis[gold_type.value] = analysis

                # 显示前几条数据
                print(f"📋 {config['name']}前5条数据预览:")
                for i, item in enumerate(gold_data[:5]):
                    print(
                        f"  {i+1}. {item['日期']} | {item['品牌']:8s} | {item['产品']:15s} | {item['价格']:8s}元/克 | {item['涨跌']} | {item['黄金类型']}"
                    )
            else:
                print(f"❌ 未能解析到{config['name']}数据")
        else:
            print(f"❌ 从新浪财经获取{config['name']}数据失败")

    # 显示汇总信息
    if all_data:
        print("\n" + "=" * 50)
        print("📈 数据获取汇总")
        print("=" * 50)

        # 按类型统计
        type_counts = {}
        for item in all_data:
            gold_type = item.get("黄金类型", "未知")
            type_counts[gold_type] = type_counts.get(gold_type, 0) + 1

        print("📊 各类型数据量:")
        for gold_type, count in type_counts.items():
            print(f"  • {gold_type}: {count} 条")

        print(f"\n🎯 总计获取: {len(all_data)} 条黄金数据")
        print("✅ 所有数据已保存到对应的JSON和Excel文件")

        # 生成合并数据文件
        try:
            from gold_data_manager import GoldDataManager

            manager = GoldDataManager()
            manager.export_combined_data()
            print("📁 合并数据已导出到 combined_gold_data.xlsx")
        except ImportError:
            print("💡 提示: 可运行 GoldDataManager 生成合并数据文件")
    else:
        print("\n❌ 未能获取到任何黄金数据")
        print("请检查网络连接或稍后重试")


if __name__ == "__main__":
    main()
