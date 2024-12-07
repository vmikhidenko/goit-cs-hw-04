import os
import time
import threading
import multiprocessing
from collections import defaultdict

def search_keywords_in_files_thread(file_list, keywords, result_dict, lock):
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for word in keywords:
                    if word in content:
                        with lock:
                            result_dict[word].append(file_path)
        except Exception as e:
            print(f"Помилка при обробці файлу {file_path}: {e}")

def multithreaded_search(file_paths, keywords, num_threads=4):
    start_time = time.time()
    threads = []
    result = defaultdict(list)
    lock = threading.Lock()

    # Розподіл файлів між потоками
    chunk_size = len(file_paths) // num_threads
    for i in range(num_threads):
        start_index = i * chunk_size
        # Останній потік бере всі залишкові файли
        if i == num_threads - 1:
            end_index = len(file_paths)
        else:
            end_index = (i + 1) * chunk_size
        thread_files = file_paths[start_index:end_index]
        thread = threading.Thread(target=search_keywords_in_files_thread, args=(thread_files, keywords, result, lock))
        threads.append(thread)
        thread.start()

    # Очікування завершення всіх потоків
    for thread in threads:
        thread.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Багатопотоковий підхід виконано за {elapsed_time:.2f} секунд.")
    return dict(result), elapsed_time

def search_keywords_in_files_process(file_list, keywords, queue):
    local_result = defaultdict(list)
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for word in keywords:
                    if word in content:
                        local_result[word].append(file_path)
        except Exception as e:
            print(f"Помилка при обробці файлу {file_path}: {e}")
    queue.put(dict(local_result))

def multiprocessing_search(file_paths, keywords, num_processes=4):
    start_time = time.time()
    processes = []
    queue = multiprocessing.Queue()
    result = defaultdict(list)

    # Розподіл файлів між процесами
    chunk_size = len(file_paths) // num_processes
    for i in range(num_processes):
        start_index = i * chunk_size
        # Останній процес бере всі залишкові файли
        if i == num_processes - 1:
            end_index = len(file_paths)
        else:
            end_index = (i + 1) * chunk_size
        process_files = file_paths[start_index:end_index]
        process = multiprocessing.Process(target=search_keywords_in_files_process, args=(process_files, keywords, queue))
        processes.append(process)
        process.start()

    # Збір результатів з черги
    for _ in processes:
        partial_result = queue.get()
        for word, files in partial_result.items():
            result[word].extend(files)

    # Очікування завершення всіх процесів
    for process in processes:
        process.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Багатопроцесорний підхід виконано за {elapsed_time:.2f} секунд.")
    return dict(result), elapsed_time

def main():
    # Задання директорії з текстовими файлами
    directory = 'texts'  # Замініть на ваш шлях

    # Перевірка існування директорії
    if not os.path.isdir(directory):
        print(f"Директорія {directory} не існує.")
        return

    # Збір всіх текстових файлів у директорії
    try:
        file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    except Exception as e:
        print(f"Помилка при зборі файлів: {e}")
        return

    if not file_paths:
        print("У вказаній директорії немає текстових файлів.")
        return

    # Задання ключових слів
    keywords = ['слово1', 'слово2', 'слово3']  # Замініть на ваші ключові слова

    print("Початок пошуку ключових слів у файлах...\n")

    # Виклик багатопотокової функції
    multithreaded_results, thread_time = multithreaded_search(file_paths, keywords, num_threads=4)
    print("\nРезультати багатопотокового пошуку:")
    for word, files in multithreaded_results.items():
        print(f"'{word}' знайдено у файлах:")
        for file in files:
            print(f"  - {file}")
    print("\n" + "-"*50 + "\n")

    # Виклик багатопроцесорної функції
    multiprocessing_results, process_time = multiprocessing_search(file_paths, keywords, num_processes=4)
    print("\nРезультати багатопроцесорного пошуку:")
    for word, files in multiprocessing_results.items():
        print(f"'{word}' знайдено у файлах:")
        for file in files:
            print(f"  - {file}")
    print("\n" + "-"*50 + "\n")

    # Порівняння часу виконання
    print(f"Час виконання багатопотокового підходу: {thread_time:.2f} секунд.")
    print(f"Час виконання багатопроцесорного підходу: {process_time:.2f} секунд.")

if __name__ == "__main__":
    main()
