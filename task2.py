from multiprocessing import Process, Manager, current_process
import os
import time
import logging

# Налаштування журналювання
logger = logging.getLogger()
logger.handlers.clear()  # Видаляємо всі обробники журналювання
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

def search_keywords_in_file(file_path, keywords, results_dict):
    result = {keyword: False for keyword in keywords}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    result[keyword] = True
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
    finally:
        results_dict[file_path] = result

def worker(file_paths, keywords, results_dict):
    name = current_process().name
    logger.debug(f'{name} started...')
    start_time = time.time()
    for file_path in file_paths:
        search_keywords_in_file(file_path, keywords, results_dict)
    end_time = time.time()
    logger.debug(f'{name} finished in {end_time - start_time:.6f} seconds.')

if __name__ == '__main__':
    logger.debug('MainProcess Started')

    file_paths = ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']  # Приклад шляхів до файлів
    keywords = ['and', 'the']

    manager = Manager()
    results_dict = manager.dict()

    num_processes = 4  # Задаємо кількість процесів, щоб обробити кожен файл окремо
    processes = []
    for i in range(num_processes):
        start_index = i * (len(file_paths) // num_processes)
        end_index = (i + 1) * (len(file_paths) // num_processes)
        process = Process(target=worker, args=(file_paths[start_index:end_index], keywords, results_dict))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = {keyword: [] for keyword in keywords}
    for file_path, result in results_dict.items():
        for keyword, found in result.items():
            if found:
                results[keyword].append(file_path)

    logger.debug(f'MainProcess Results: {results}')