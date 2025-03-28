from collections import deque, Counter
import random

def generate_memory_requests(n, max_page):
    return [random.randint(0, max_page - 1) for _ in range(n)]

def parse_memory_requests(input_str):
    try:
        return [int(page.strip()) for page in input_str.split(",") if page.strip()]
    except ValueError:
        print("Invalid input format. Please enter comma-separated integers.")
        return None

class SingleLevelPaging:
    def __init__(self, frame_count):
        self.page_table = {}
        self.frames = frame_count
        self.memory = deque(maxlen=frame_count)

    def access_page(self, page):
        if page in self.page_table:
            return "Page Hit"
        if len(self.memory) >= self.frames:
            removed_page = self.memory.popleft()
            del self.page_table[removed_page]
        self.memory.append(page)
        self.page_table[page] = len(self.memory) - 1
        return "Page Fault"

def run_simulation():
    # Input handling (same as before)
    total_physical_frames = 3
    tlb_size = 2
    memory_requests = [1, 2, 3, 4, 1, 2, 5]
    total_access_requests = len(memory_requests)

    paging = SingleLevelPaging(total_physical_frames)
    tlb_hits = tlb_misses = page_faults = 0
    tlb_cache = deque(maxlen=tlb_size)  # FIFO cache
    
    for page in memory_requests:
        # Check TLB FIRST
        tlb_hit = False
        if page in tlb_cache:
            tlb_hits += 1
            tlb_hit = True
            # Move to end to maintain order (LRU-like)
            tlb_cache.remove(page)
            tlb_cache.append(page)
        else:
            tlb_misses += 1
            tlb_cache.append(page)
        
        # Then process page access
        result = paging.access_page(page)
        if result == "Page Fault":
            page_faults += 1

    print(f"TLB Hits: {tlb_hits}")
if __name__ == "__main__":
    run_simulation()