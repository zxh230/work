import re
import os

def convert_md_to_html(md_content):
    # 正则表达式匹配Markdown图片链接
    pattern = r'!\[(.*?)\]\((.*?)\)'
    html_content = re.sub(pattern, r'<img src="\2" alt="\1">', md_content)
    return html_content

def process_md_files(input_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有.md文件
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.md'):
                md_file_path = os.path.join(root, file)
                # 读取Markdown文件内容
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                # 转换Markdown内容为HTML
                html_content = convert_md_to_html(md_content)

                # 输出变更内容供用户确认
                if md_content != html_content:
                    print(f"文件 {file} 的变更内容如下：")
                    print("-" * 50)
                    import difflib
                    diff = difflib.unified_diff(md_content.splitlines(), html_content.splitlines(), lineterm='')
                    for line in diff:
                        print(line)
                    print("-" * 50)
                    confirm = input("确认变更内容是否正确？(y/n): ")
                    if confirm.lower() != 'y':
                        print(f"跳过文件 {file} 的保存。")
                        continue

                # 生成输出文件路径
                html_file_name = os.path.splitext(file)[0] + '.html'
                html_file_path = os.path.join(output_folder, html_file_name)

                # 保存转换后的HTML内容到新文件
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"文件 {file} 转换并保存成功。")

if __name__ == "__main__":
    input_folder = '.'  # 当前文件夹
    output_folder = 'output'  # 输出文件夹
    process_md_files(input_folder, output_folder)
