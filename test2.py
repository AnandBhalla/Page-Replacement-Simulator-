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
    memory_requests = generate_memory_requests(20, 10)
    frames = 3
    paging_type = SingleLevelPaging(frames)
    print("\nMemory Requests:", memory_requests)
    
    # Simulate Paging
    page_faults = sum([paging_type.access_page(p) == "Page Fault" for p in memory_requests])
    print(f"Page Faults (Single-Level Paging): {page_faults}")
    
    # Page Replacement Simulation
    print(f"FIFO Page Faults: {fifo_replacement(memory_requests, frames)}")
    print(f"LRU Page Faults: {lru_replacement(memory_requests, frames)}")
    print(f"LFU Page Faults: {lfu_replacement(memory_requests, frames)}")
    print(f"Optimal Page Faults: {optimal_replacement(memory_requests, frames)}")

if __name__ == "__main__":
    run_simulation()
