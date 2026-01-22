import re
from process.models import ErrorCorrection, departments


def extract_and_correct(raw_text):
    # 1. 自动纠错逻辑：从数据库读取并替换
    corrections = ErrorCorrection.objects.all()
    department_pattern = departments.objects.all()
    corrected_text = raw_text
    for item in corrections:
        corrected_text = corrected_text.replace(item.error_word, item.correct_word)

    for item in department_pattern:
        corrected_text = corrected_text.replace(item.full_name, item.short_name)

    # 2. 提取信息逻辑 (使用正则表达式)
    # 提取文件编号: 匹配如 [2023] 1号 或 国办发〔2023〕12号
    num_pattern = r'([A-Za-z0-9\u4e00-\u9fa5]+〔?\d{4}〕?\d+号)'
    # 提取文件标题: 匹配 “关于......的通知/函/批复”
    title_pattern = r'(关于.*?(?:通知|函|批复|意见|报告))'
    # 提取来文单位: 简单匹配首行或特定关键词后的内容（此处建议根据实际格式调整）
    unit_pattern = r'^([\u4e00-\u9fa5]{2,30}(?:厅|部|局|办公室|委|公司))'

    file_no = re.search(num_pattern, corrected_text)
    file_title = re.search(title_pattern, corrected_text)
    file_unit = re.search(unit_pattern, corrected_text)

    return {
        "title": file_title.group(0) if file_title else "",
        "number": file_no.group(0) if file_no else "",
        "unit": file_unit.group(0) if file_unit else "",
        "full_text": corrected_text
    }