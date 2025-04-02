from collections import deque, Counter
import random

def generate_memory_requests(n, max_page):
    return [random.randint(0, max_page - 1) for _ in range(n)]

# Paging Mechanisms
class SingleLevelPaging:
    def __init__(self, frame_count):
        self.page_table = {}  # Page -> Frame
        self.frames = frame_count
        self.memory = set()

    def access_page(self, page):
        if page in self.page_table:
            return "Page Hit"
        if len(self.memory) >= self.frames:
            self.memory.pop()
        self.memory.add(page)
        self.page_table[page] = len(self.memory) - 1
        return "Page Fault"

class MultiLevelPaging:
    def __init__(self, frame_count):
        self.page_directory = {}  # Directory -> Page Table -> Frame
        self.frames = frame_count
        self.memory = set()

    def access_page(self, page):
        dir_index = page // 10  # Example: Assume each directory holds 10 pages
        if dir_index not in self.page_directory:
            self.page_directory[dir_index] = {}
        if page in self.page_directory[dir_index]:
            return "Page Hit"
        if len(self.memory) >= self.frames:
            self.memory.pop()
        self.memory.add(page)
        self.page_directory[dir_index][page] = len(self.memory) - 1
        return "Page Fault"

class InvertedPaging:
    def __init__(self, frame_count):
        self.frame_table = {}  # Frame -> Page
        self.frames = frame_count
        self.reverse_map = {}  # Page -> Frame Lookup

    def access_page(self, page):
        if page in self.reverse_map:
            return "Page Hit"
        if len(self.frame_table) >= self.frames:
            removed = next(iter(self.frame_table))
            del self.frame_table[removed]
            del self.reverse_map[removed]
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
    page_table_type = input("Enter page table type (single/multi/inverted): ").strip().lower()
    tlb_size = int(input("Enter TLB size: "))
    replacement_algo = input("Enter replacement algorithm (FIFO/LRU/LFU/Optimal): ").strip().lower()
    total_access_requests = int(input("Enter total memory access requests: "))
    
    memory_requests = generate_memory_requests(total_access_requests, total_virtual_pages)
    
    if page_table_type == "single":
        paging = SingleLevelPaging(total_physical_frames)
    elif page_table_type == "multi":
        paging = MultiLevelPaging(total_physical_frames)
    elif page_table_type == "inverted":
        paging = InvertedPaging(total_physical_frames)
    else:
        print("Invalid page table type!")
        return
    
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
    
    if replacement_algo == "fifo":
        replacement_faults = fifo_replacement(memory_requests, total_physical_frames)
    elif replacement_algo == "lru":
        replacement_faults = lru_replacement(memory_requests, total_physical_frames)
    elif replacement_algo == "lfu":
        replacement_faults = lfu_replacement(memory_requests, total_physical_frames)
    elif replacement_algo == "optimal":
        replacement_faults = optimal_replacement(memory_requests, total_physical_frames)
    else:
        print("Invalid replacement algorithm!")
        return
    
    print(f"\nTotal Page Faults: {page_faults}")
    print(f"TLB Hits: {tlb_hits}, TLB Misses: {tlb_misses}")
    print(f"Page Faults using {replacement_algo.upper()}: {replacement_faults}")
    print(f"Page Fault Rate: {page_faults / total_access_requests:.2f}")
    print(f"TLB Hit Ratio: {tlb_hits / total_access_requests:.2f}")

if __name__ == "__main__":
    run_simulation()
