import os

from similar_code import find_similar_code


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def find_md_files(md_folder, exclude_folders):
    md_files = []

    for root, dirs, files in os.walk(md_folder):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files


def save_recommendation_to_file(recommendation, recommendation_number):
    filename = os.path.join(RECOMMENDATIONS_PATH, f"recommendation_{recommendation_number}.md")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(recommendation)

def split_recommendations(file_path):
    existing_recommendations = read_file(file_path)
    split_recommendations = existing_recommendations.split('\n```\n')
    for i, recommendation in enumerate(split_recommendations[:-1], start=1):
        recommendation += '\n```'
        save_recommendation_to_file(recommendation, i)

    os.remove(file_path)

    # end_recommendation_index = existing_recommendations.find('```\n', 0, prev_newline_index)


exclude_folders = ['notes']
RECOMMENDATIONS_PATH = 'D:\Projects\React Native\AppTS\docs/notes\Similar Code/'
def main(md_folder, recommend_file):
    # Создайте или очистите рекомендуемый файл
    with open(recommend_file, 'w') as rec_file:
        rec_file.write('')

    # Список .md файлов
    md_files = find_md_files(md_folder, exclude_folders)
    print(md_files)
    processed_pairs = set()  # Множество для отслеживания обработанных пар

    # Вызовите find_similar_code() для каждой пары файлов
    for i, src_file in enumerate(md_files):
        for j, target_file in enumerate(md_files):
            if i != j:
                # Создаем уникальный идентификатор для пары файлов, чтобы избежать дублирования
                file_pair = (src_file, target_file)
                reverse_file_pair = (target_file, src_file)

                if file_pair not in processed_pairs and reverse_file_pair not in processed_pairs:
                    # Эта пара файлов еще не была обработана
                    find_similar_code(os.path.join(md_folder, src_file), os.path.join(md_folder, target_file),
                                      recommend_file)
                    processed_pairs.add(file_pair)
                    processed_pairs.add(reverse_file_pair)

    split_recommendations(recommend_file)



if __name__ == '__main__':
    md_folder = 'D:\Projects\React Native\AppTS\docs'  # Замените на путь к папке с вашими .md файлами
    recommend_file = RECOMMENDATIONS_PATH + 'recommend.md'  # Название файла для рекомендаций

    main(md_folder, recommend_file)
