import os
import time
import threading
from multiprocessing import Process, Queue, cpu_count

# Пошук ключових слів у файлах
def search_keywords(file_paths, keywords):
    results = {kw: [] for kw in keywords}
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for kw in keywords:
                    if kw in content:
                        results[kw].append(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return results

# Функція для багатопотокової реалізації
def threaded_search(file_paths, keywords):
    num_threads = min(len(file_paths), 8)  # Макс. 8 потоків або кількість файлів
    chunk_size = len(file_paths) // num_threads
    threads = []
    results = {kw: [] for kw in keywords}
    lock = threading.Lock()

    def thread_task(chunk):
        local_results = search_keywords(chunk, keywords)
        with lock:
            for kw, files in local_results.items():
                results[kw].extend(files)

    for i in range(num_threads):
        chunk = file_paths[i * chunk_size: (i + 1) * chunk_size]
        t = threading.Thread(target=thread_task, args=(chunk,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return results

# Функція для багатопроцесорної реалізації
def process_task(chunk, keywords, queue):
    local_results = search_keywords(chunk, keywords)
    queue.put(local_results)

def multiprocessing_search(file_paths, keywords):
    num_processes = min(cpu_count(), len(file_paths))
    chunk_size = len(file_paths) // num_processes
    processes = []
    queue = Queue()

    for i in range(num_processes):
        chunk = file_paths[i * chunk_size: (i + 1) * chunk_size]
        p = Process(target=process_task, args=(chunk, keywords, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = {kw: [] for kw in keywords}
    while not queue.empty():
        local_results = queue.get()
        for kw, files in local_results.items():
            results[kw].extend(files)

    return results

# Основна функція
def main():
    keywords = ['keyword1', 'keyword2', 'keyword3']  # Ключові слова
    directory = './files'  # Директорія з файлами
    file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    print("Starting threaded search...")
    start = time.time()
    thread_results = threaded_search(file_paths, keywords)
    print(f"Threaded search completed in {time.time() - start:.2f}s\n")

    print("Starting multiprocessing search...")
    start = time.time()
    process_results = multiprocessing_search(file_paths, keywords)
    print(f"Multiprocessing search completed in {time.time() - start:.2f}s\n")

    print("Results (Threading):", thread_results)
    print("Results (Multiprocessing):", process_results)

if __name__ == '__main__':
    main()