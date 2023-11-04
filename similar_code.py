import difflib
import re
import os

def find_similar_code(src_file, target_file, recommend_file):
    src_text_file = read_file(src_file)
    code_lang = find_code_lang(src_text_file)
    src_text = read_code_block(src_file)
    target_text = read_code_block(target_file)

    src_lines = src_text.splitlines()
    target_lines = target_text.splitlines()
    matcher = difflib.SequenceMatcher(None, src_lines, target_lines)
    similar_code = find_similar_lines(matcher, target_lines)
    validated_similar_code = validate_similar_code(similar_code)
    existing_code = read_file(recommend_file)
    new_code = filter_and_join_code(validated_similar_code)

    if new_code not in existing_code and len(new_code) > 0:
        append_code_to_recommend_file(recommend_file, new_code, code_lang, src_file, target_file)
    else:
        update_recommend_file_info(recommend_file, new_code, src_file, target_file)


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def validate_similar_code(similar_code):
    code_concatenated = ''.join(element.strip() for element in similar_code)
    return similar_code if len(code_concatenated) > 30 else ''


def find_similar_lines(matcher, target_lines):
    similar_code = []

    for op, _, _, target_start, target_end in matcher.get_opcodes():
        if op == 'equal':
            similar_lines = target_lines[target_start:target_end]
            if len(similar_lines) > 1:
                similar_code.extend(similar_lines)

    return similar_code



def filter_and_join_code(similar_code):
    code_without_backticks = '\n'.join(similar_code).replace('```', '')
    new_code_lines = [line for line in code_without_backticks.split('\n') if len(line.split()) > 1]
    return '\n'.join(new_code_lines)


def append_code_to_recommend_file(recommend_file, new_code, code_lang, src_file, target_file):
    with open(recommend_file, 'a', encoding='utf-8') as rec_file:
        src_file_name = src_file.split('\\')[-1]
        target_file_name = target_file.split('\\')[-1]
        src_relative = os.path.relpath(src_file, os.path.dirname(recommend_file)).replace('\\', '/')
        target_relative = os.path.relpath(target_file, os.path.dirname(recommend_file)).replace('\\', '/')
        rec_file.write(f"File: [{src_file_name}]({src_relative})\n")
        rec_file.write(f"File: [{target_file_name}]({target_relative})\n\n")
        rec_file.write(code_lang + '\n')
        rec_file.write(new_code)
        rec_file.write('\n```')
        rec_file.write('\n\n')


def update_recommend_file_info(recommend_file, new_code, src_file, target_file):
    with open(recommend_file, 'r', encoding='utf-8') as rec_file:
        existing_code = rec_file.read()

    if len(new_code) > 0:
        index = existing_code.find(new_code)
        prev_newline_index = existing_code.rfind('\n```', 0, index)
        prev_element_index = existing_code.rfind('```\n', 0, prev_newline_index)
        src_file_name = src_file.split('\\')[-1]
        target_file_name = target_file.split('\\')[-1]

        src_relative = os.path.relpath(src_file, os.path.dirname(recommend_file)).replace('\\', '/')
        target_relative = os.path.relpath(target_file, os.path.dirname(recommend_file)).replace('\\', '/')

        src = f"File: [{src_file_name}]({src_relative})\n"
        target = f"File: [{target_file_name}]({target_relative})\n"

        if prev_newline_index != -1 and prev_newline_index > prev_element_index:
            existing_text_between = existing_code[(prev_element_index if prev_element_index != -1 else 0):prev_newline_index]

            if src in existing_text_between:
                src = ''

            if target in existing_text_between:
                target = ''

        info_to_append = src + target
        updated_existing_code = existing_code[:prev_newline_index] + info_to_append + existing_code[prev_newline_index:]

        with open(recommend_file, 'w', encoding='utf-8') as rec_file:
            rec_file.write(updated_existing_code)

def find_code_lang(src_text):
    pattern = r'```[\w\s]+(?=\n|$)'
    match = re.search(pattern, src_text)
    return match.group(0) if match else ''

def read_code_block(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()
        code_block_pattern = r'```[\w\s]+\n(.*?)```'
        match = re.search(code_block_pattern, file_contents, re.DOTALL)
        if match:
            code_block = match.group(1)
            import_pattern = r'^\s*import\s.*;$'
            lines = code_block.split('\n')
            filtered_lines = [line for line in lines if not re.match(import_pattern, line)]
            modified_code_block = '\n'.join(filtered_lines)
            return modified_code_block
        else:
            return ''
