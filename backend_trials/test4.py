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
    # Configuration matching your test case
    memory_requests = [1, 2, 3, 4, 1, 2, 5]
    total_physical_frames = 3
    tlb_size = 2
    
    # Initialize counters
    tlb_hits = 0
    tlb_misses = 0
    page_faults = 0
    
    # Use a deque for TLB with maxlen for automatic FIFO eviction
    tlb_cache = deque(maxlen=tlb_size)
    
    # Use a separate deque for page frames
    memory_frames = deque(maxlen=total_physical_frames)
    
    for page in memory_requests:
        # Check TLB first - this is critical
        tlb_hit = False
        if page in tlb_cache:
            tlb_hits += 1
            tlb_hit = True
            # Move to end to maintain access order
            tlb_cache.remove(page)
            tlb_cache.append(page)
        
        if not tlb_hit:
            tlb_misses += 1
            tlb_cache.append(page)
        
        # Process page access
        if page not in memory_frames:
            page_faults += 1
            memory_frames.append(page)
    
    print(f"\nResults for SINGLE Paging:")
    print(f"Total Page Faults: {page_faults}")
    print(f"TLB Hits: {tlb_hits}, TLB Misses: {tlb_misses}")
    print(f"Page Fault Rate: {page_faults / len(memory_requests):.2f}")
    print(f"TLB Hit Ratio: {tlb_hits / len(memory_requests):.2f}")
    print(f"Page Faults using FIFO: {page_faults}")

if __name__ == "__main__":
    run_simulation()