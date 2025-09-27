import pandas as pd
from datetime import datetime
from config.config import Config

class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_report(results):
        """生成处理报告"""
        timestamp = datetime.now().strftime(Config.REPORT_TIMESTAMP_FORMAT)
        report_filename = f'处理报告_{timestamp}.xlsx'
        
        try:
            with pd.ExcelWriter(report_filename, engine='openpyxl') as writer:
                # 创建各个状态的DataFrame并写入不同的sheet
                sheet_names = {
                    'pending_review': '待审核',
                    'completed': '已完成',
                    'newly_submitted': '新提交',
                    'failed': '提交失败'
                }
                
                for status, data in results.items():
                    if data:  # 只处理有数据的状态
                        df = pd.DataFrame(data)
                        sheet_name = sheet_names.get(status, status)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # 自动调整列宽
                        worksheet = writer.sheets[sheet_name]
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"\n✅ 处理报告已生成: {report_filename}")
            return report_filename
            
        except Exception as e:
            print(f"❌ 生成报告时发生错误: {str(e)}")
            return None
    
    @staticmethod
    def print_summary(results):
        """打印处理摘要"""
        total = sum(len(data) for data in results.values())
        
        print(f"\n📊 处理摘要:")
        print(f"{'='*50}")
        print(f"📋 总学生数: {total}")
        print(f"✅ 已完成: {len(results.get('completed', []))} 人")
        print(f"⏳ 待审核: {len(results.get('pending_review', []))} 人")
        print(f"🆕 新提交: {len(results.get('newly_submitted', []))} 人")
        print(f"❌ 提交失败: {len(results.get('failed', []))} 人")
        
        if total > 0:
            success_rate = ((total - len(results.get('failed', []))) / total * 100)
            print(f"📈 成功率: {success_rate:.1f}%")
        
        print(f"{'='*50}")
        
        # 如果有失败的，显示失败原因统计
        failed_data = results.get('failed', [])
        if failed_data:
            print(f"\n❌ 失败原因统计:")
            error_counts = {}
            for item in failed_data:
                error = item.get('错误信息', '未知错误')
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {error}: {count} 人") 