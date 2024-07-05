from threading import Thread, RLock
import logging
from time import time, sleep
from itertools import islice

# Налаштування журналювання
logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

lock = RLock()

def search_keywords_in_file(file_path, keywords):
    results = {keyword: [] for keyword in keywords}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    results[keyword].append(file_path)
        sleep(0.1)  # Додано затримку для вимірювання часу виконання
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
    return results

def worker(file_paths, keywords, results, locker):
    for file_path in file_paths:
        logging.debug(f"Thread started for {file_path}")
        timer = time()
        file_results = search_keywords_in_file(file_path, keywords)
        with locker:
            for keyword, paths in file_results.items():
                if paths:
                    results[keyword].extend(paths)
        logging.debug(f"Done {file_path} in {time() - timer:.6f} seconds")

def chunked_iterable(iterable, size):
    iterator = iter(iterable)
    for first in iterator:
        yield [first] + list(islice(iterator, size - 1))

def main_threading(file_paths, keywords):
    start_time = time()
    
    results = {keyword: [] for keyword in keywords}
    threads = []
    num_threads = 4  # Кількість потоків
    chunk_size = len(file_paths) // num_threads + (len(file_paths) % num_threads > 0)
    
    for chunk in chunked_iterable(file_paths, chunk_size):
        thread = Thread(target=worker, args=(chunk, keywords, results, lock))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time()
    logging.debug(f"Threading approach took {end_time - start_time:.6f} seconds")
    return results

if __name__ == '__main__':
    logging.debug('Started')
    # Приклад використання
    file_paths = ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']  # Приклад шляхів до файлів
    keywords = ['and', 'the']
    results_threading = main_threading(file_paths, keywords)
    logging.debug(f"Results: {results_threading}")
