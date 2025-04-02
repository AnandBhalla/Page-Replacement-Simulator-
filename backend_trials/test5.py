from collections import deque, Counter
import random

def generate_memory_requests(n, max_page):
    return [random.randint(0, max_page - 1) for _ in range(n)]

# Paging Mechanisms
class SingleLevelPaging:
    def __init__(self, frame_count):
        self.page_table = {}  # {page_number: frame_number}
        self.frames = frame_count
        self.memory = deque()

    def access_page(self, page):
        if page in self.page_table:
            return "Page Hit"
        if len(self.memory) >= self.frames:
            removed_page = self.memory.popleft()
            del self.page_table[removed_page]
        self.memory.append(page)
        self.page_table[page] = len(self.memory) - 1
        return "Page Fault"

class MultiLevelPaging:
    def __init__(self, frame_count):
        self.page_directory = {}  # {dir_index: {page_number: frame_number}}
        self.frames = frame_count
        self.memory = deque()

    def access_page(self, page):
        dir_index = page // 10
        if dir_index not in self.page_directory:
            self.page_directory[dir_index] = {}

        if page in self.page_directory[dir_index]:
            return "Page Hit"

        if len(self.memory) >= self.frames:
            removed_page = self.memory.popleft()
            removed_dir_index = removed_page // 10
            del self.page_directory[removed_dir_index][removed_page]

        self.memory.append(page)
        self.page_directory[dir_index][page] = len(self.memory) - 1
        return "Page Fault"

class InvertedPaging:
    def __init__(self, frame_count):
        self.frame_table = {}  # {frame_number: page_number}
        self.frames = frame_count
        self.reverse_map = {}

    def access_page(self, page):
        if page in self.reverse_map:
            return "Page Hit"
        if len(self.frame_table) >= self.frames:
            removed_frame = next(iter(self.frame_table))
            removed_page = self.frame_table[removed_frame]
            del self.frame_table[removed_frame]
            del self.reverse_map[removed_page]

        frame_number = len(self.frame_table)
        self.frame_table[frame_number] = page
        self.reverse_map[page] = frame_number
        return "Page Fault"

# Page Replacement Algorithms
def fifo_replacement(pages, frames):
    memory = deque()
    page_faults = 0
    for page in pages:
        if page not in memory:
            if len(memory) >= frames:
                memory.popleft()
            memory.append(page)
            page_faults += 1
    return page_faults

def lru_replacement(pages, frames):
    memory = []
    page_faults = 0
    for page in pages:
        if page in memory:
            memory.remove(page)
        else:
            if len(memory) >= frames:
                memory.pop(0)
            page_faults += 1
        memory.append(page)
    return page_faults

def lfu_replacement(pages, frames):
    memory = set()
    frequency = Counter()
    page_faults = 0
    for page in pages:
        if page not in memory:
            if len(memory) >= frames:
                least_used = min(memory, key=lambda x: frequency[x])
                memory.remove(least_used)
                del frequency[least_used]
            memory.add(page)
            page_faults += 1
        frequency[page] += 1
    return page_faults

def optimal_replacement(pages, frames):
    memory = []
    page_faults = 0
    for i, page in enumerate(pages):
        if page not in memory:
            if len(memory) >= frames:
                future_uses = {p: pages[i+1:].index(p) if p in pages[i+1:] else float('inf') for p in memory}
                memory.remove(max(future_uses, key=future_uses.get))
            page_faults += 1
            memory.append(page)
    return page_faults

def run_simulation():
    total_virtual_pages = int(input("Enter total virtual pages: "))
    total_physical_frames = int(input("Enter total physical frames: "))
    page_size = int(input("Enter page size (bytes): "))
    page_table_type = input("Enter page table type (single/multi/inverted/all): ").strip().lower()
    tlb_size = int(input("Enter TLB size: "))
    replacement_algo = input("Enter replacement algorithm (FIFO/LRU/LFU/Optimal/All): ").strip().lower()
    total_access_requests = int(input("Enter total memory access requests: "))
    
    memory_requests = generate_memory_requests(total_access_requests, total_virtual_pages)
    
    page_types = {
        "single": SingleLevelPaging,
        "multi": MultiLevelPaging,
        "inverted": InvertedPaging
    }
    
    if page_table_type == "all":
        selected_page_types = page_types
    else:
        selected_page_types = {page_table_type: page_types[page_table_type]} if page_table_type in page_types else {}
    
    replacement_algos = {
        "fifo": fifo_replacement,
        "lru": lru_replacement,
        "lfu": lfu_replacement,
        "optimal": optimal_replacement
    }
    
    if replacement_algo == "all":
        selected_algorithms = replacement_algos
    else:
        selected_algorithms = {replacement_algo: replacement_algos[replacement_algo]} if replacement_algo in replacement_algos else {}
    
    for p_type, PagingClass in selected_page_types.items():
        paging = PagingClass(total_physical_frames)
        tlb_hits, tlb_misses, page_faults = 0, 0, 0
        tlb_cache = {}
        
        for page in memory_requests:
            if page in tlb_cache:
                tlb_hits += 1
            else:
                tlb_misses += 1
                result = paging.access_page(page)
                if result == "Page Fault":
                    page_faults += 1
                if len(tlb_cache) >= tlb_size:
                    tlb_cache.pop(next(iter(tlb_cache)))
                tlb_cache[page] = True
        
        print(f"\nResults for {p_type.upper()} Paging:")
        print(f"Total Page Faults: {page_faults}")
        print(f"TLB Hits: {tlb_hits}, TLB Misses: {tlb_misses}")
        print(f"Page Fault Rate: {page_faults / total_access_requests:.2f}")
        print(f"TLB Hit Ratio: {tlb_hits / total_access_requests:.2f}")
        
        # Display Full Page Table
        print("\nFinal Page Table:")
        if p_type == "single":
            print("Page -> Frame")
            for page, frame in paging.page_table.items():
                print(f"{page} -> {frame}")
        elif p_type == "multi":
            print("Directory -> (Page -> Frame)")
            for dir_index, pages in paging.page_directory.items():
                print(f"{dir_index} -> {pages}")
        elif p_type == "inverted":
            print("Frame -> Page")
            for frame, page in paging.frame_table.items():
                print(f"{frame} -> {page}")
        
        print("\n" + "-"*50)

        for algo, func in selected_algorithms.items():
            replacement_faults = func(memory_requests, total_physical_frames)
            print(f"Page Faults using {algo.upper()}: {replacement_faults}")

if __name__ == "__main__":
    run_simulation()
