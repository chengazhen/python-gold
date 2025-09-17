"""
黄金数据管理器
用于管理不同类型的黄金数据，提供统一的接口
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from xinlang import (
    GoldType,
    GoldDataConfig,
    fetch_gold_data_from_sina,
    parse_complete_gold_data,
    analyze_gold_data,
)


class GoldDataManager:
    """黄金数据管理器"""

    def __init__(self, data_dir: str = "."):
        """初始化数据管理器

        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def fetch_and_save_data(
        self, gold_type: GoldType, custom_params: dict = None
    ) -> bool:
        """获取并保存指定类型的黄金数据

        Args:
            gold_type: 黄金类型
            custom_params: 自定义参数

        Returns:
            bool: 是否成功
        """
        try:
            config = GoldDataConfig.get_config(gold_type)
            print(f"正在获取{config['name']}数据...")

            # 获取数据
            html_text = fetch_gold_data_from_sina(
                gold_type, custom_params=custom_params
            )
            if not html_text:
                print(f"❌ 获取{config['name']}数据失败")
                return False

            # 解析数据
            gold_data = parse_complete_gold_data(html_text, gold_type)
            if not gold_data:
                print(f"❌ 解析{config['name']}数据失败")
                return False

            # 分析数据
            analysis = analyze_gold_data(gold_data)

            # 保存数据
            self._save_data(gold_data, analysis, gold_type)

            print(f"✅ 成功获取并保存 {len(gold_data)} 条{config['name']}数据")
            return True

        except Exception as e:
            print(f"❌ 处理{config['name']}数据时发生错误: {e}")
            return False

    def _save_data(self, gold_data: List[Dict], analysis: Dict, gold_type: GoldType):
        """保存数据到文件"""

        # 生成文件路径
        json_file = self.data_dir / GoldDataConfig.get_filename(
            gold_type, "json", timestamp=False
        )
        analysis_file = self.data_dir / GoldDataConfig.get_filename(
            gold_type, "json", timestamp=False
        ).replace(".json", "_analysis.json")
        excel_file = self.data_dir / GoldDataConfig.get_filename(
            gold_type, "xlsx", timestamp=False
        )

        # 带时间戳的文件
        json_file_ts = self.data_dir / GoldDataConfig.get_filename(
            gold_type, "json", timestamp=True
        )
        analysis_file_ts = self.data_dir / GoldDataConfig.get_filename(
            gold_type, "json", timestamp=True
        ).replace(".json", "_analysis.json")

        # 保存JSON数据
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(gold_data, f, ensure_ascii=False, indent=2)

        with open(json_file_ts, "w", encoding="utf-8") as f:
            json.dump(gold_data, f, ensure_ascii=False, indent=2)

        # 保存分析结果
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        with open(analysis_file_ts, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        # 保存Excel文件
        try:
            df = pd.DataFrame(gold_data)
            df.to_excel(excel_file, index=False)
            print(f"📁 数据已保存到: {json_file}, {analysis_file}, {excel_file}")
        except ImportError:
            print(f"📁 数据已保存到: {json_file}, {analysis_file}")
            print("   注意: 需要安装pandas才能保存Excel文件")

    def load_data(self, gold_type: GoldType) -> Optional[List[Dict]]:
        """加载指定类型的黄金数据

        Args:
            gold_type: 黄金类型

        Returns:
            数据列表或None
        """
        json_file = self.data_dir / GoldDataConfig.get_filename(
            gold_type, "json", timestamp=False
        )

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(
                f"❌ 未找到{GoldDataConfig.get_config(gold_type)['name']}数据文件: {json_file}"
            )
            return None
        except Exception as e:
            print(f"❌ 加载数据时发生错误: {e}")
            return None

    def get_all_data_summary(self) -> Dict:
        """获取所有类型黄金数据的汇总信息"""
        summary = {}

        for gold_type in GoldType:
            config = GoldDataConfig.get_config(gold_type)
            data = self.load_data(gold_type)

            if data:
                summary[gold_type.value] = {
                    "name": config["name"],
                    "count": len(data),
                    "latest_date": max([item.get("日期", "") for item in data]),
                    "brands": len(set([item.get("品牌", "") for item in data])),
                    "avg_price": (
                        sum(
                            [
                                item.get("价格_数值", 0)
                                for item in data
                                if item.get("价格_数值")
                            ]
                        )
                        / len([item for item in data if item.get("价格_数值")])
                        if any(item.get("价格_数值") for item in data)
                        else 0
                    ),
                }
            else:
                summary[gold_type.value] = {
                    "name": config["name"],
                    "count": 0,
                    "latest_date": "无数据",
                    "brands": 0,
                    "avg_price": 0,
                }

        return summary

    def compare_gold_types(self) -> Dict:
        """比较不同类型黄金的价格"""
        comparison = {}

        for gold_type in GoldType:
            data = self.load_data(gold_type)
            config = GoldDataConfig.get_config(gold_type)

            if data:
                prices = [
                    item.get("价格_数值", 0) for item in data if item.get("价格_数值")
                ]
                if prices:
                    comparison[gold_type.value] = {
                        "name": config["name"],
                        "max_price": max(prices),
                        "min_price": min(prices),
                        "avg_price": sum(prices) / len(prices),
                        "count": len(prices),
                    }

        return comparison

    def export_combined_data(self, output_file: str = "combined_gold_data.xlsx"):
        """导出所有类型的黄金数据到一个Excel文件"""
        try:
            with pd.ExcelWriter(
                self.data_dir / output_file, engine="openpyxl"
            ) as writer:

                # 为每种黄金类型创建一个工作表
                for gold_type in GoldType:
                    data = self.load_data(gold_type)
                    config = GoldDataConfig.get_config(gold_type)

                    if data:
                        df = pd.DataFrame(data)
                        sheet_name = config["name"]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        print(f"✅ {config['name']}数据已导出到工作表: {sheet_name}")

                # 创建汇总工作表
                summary = self.get_all_data_summary()
                summary_df = pd.DataFrame.from_dict(summary, orient="index")
                summary_df.to_excel(writer, sheet_name="数据汇总", index=True)

                print(f"📊 所有数据已导出到: {output_file}")

        except ImportError:
            print("❌ 需要安装pandas和openpyxl才能导出Excel文件")
        except Exception as e:
            print(f"❌ 导出数据时发生错误: {e}")


def main():
    """自动获取所有类型黄金数据"""
    manager = GoldDataManager()

    print("黄金数据管理器 - 自动获取所有类型数据")
    print("=" * 50)
    print("🔄 正在从新浪财经获取所有类型黄金数据...")
    print("=" * 50)

    # 获取所有类型的数据
    success_count = 0
    for gold_type in GoldType:
        config = GoldDataConfig.get_config(gold_type)
        print(f"\n📊 正在处理: {config['name']}")
        if manager.fetch_and_save_data(gold_type):
            success_count += 1

    # 显示汇总信息
    print("\n" + "=" * 50)
    print("📈 数据获取汇总")
    print("=" * 50)

    if success_count > 0:
        summary = manager.get_all_data_summary()
        print("📊 各类型数据统计:")
        total_records = 0
        for gold_type, info in summary.items():
            if info["count"] > 0:
                print(
                    f"  • {info['name']}: {info['count']}条记录, 平均价格: {info['avg_price']:.2f}元/克"
                )
                total_records += info["count"]

        print(f"\n🎯 总计获取: {total_records} 条黄金数据")

        # 比较不同类型
        print("\n📊 价格比较:")
        comparison = manager.compare_gold_types()
        for gold_type, info in comparison.items():
            print(
                f"  • {info['name']}: 最高{info['max_price']:.2f}, 最低{info['min_price']:.2f}, 平均{info['avg_price']:.2f}元/克"
            )

        # 导出合并数据
        print(f"\n📁 正在导出合并数据...")
        manager.export_combined_data()
        print("✅ 所有数据处理完成!")
    else:
        print("❌ 未能获取到任何数据，请检查网络连接或稍后重试")


if __name__ == "__main__":
    main()
