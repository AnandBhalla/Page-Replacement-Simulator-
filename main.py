from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import deque, Counter, OrderedDict, defaultdict
import random
from typing import List, Dict

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_memory_requests(n: int, max_page: int) -> List[int]:
    return [random.randint(0, max_page - 1) for _ in range(n)]

def parse_memory_requests(input_str: str) -> List[int]:
    try:
        return [int(page.strip()) for page in input_str.split(",") if page.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory requests format - must be comma-separated integers")

# Paging Mechanism (Single Level Only)
class SingleLevelPaging:
    def __init__(self, frame_count: int):
        self.frames = frame_count
        self.memory = OrderedDict()  # Using OrderedDict for LRU tracking
        self.page_faults = 0

    def access_page(self, page: int) -> str:
        if page in self.memory:
            self.memory.move_to_end(page)  # Mark as recently used
            return "Page Hit"
        
        self.page_faults += 1
        if len(self.memory) >= self.frames:
            self.memory.popitem(last=False)  # Remove least recently used
        self.memory[page] = True  # Add new page at MRU position
        return "Page Fault"

# Updated Page Replacement Algorithms
def fifo_replacement(pages: List[int], frames: int) -> int:
    memory = set()
    queue = deque()
    page_faults = 0

    for page in pages:
        if page in memory:
            continue

        page_faults += 1
        if len(memory) >= frames:
            oldest = queue.popleft()
            memory.remove(oldest)

        memory.add(page)
        queue.append(page)

    return page_faults

def lru_replacement(pages: List[int], frames: int) -> int:
    memory = OrderedDict()
    page_faults = 0

    for page in pages:
        if page in memory:
            memory.move_to_end(page)
            continue

        page_faults += 1
        if len(memory) >= frames:
            memory.popitem(last=False)
        memory[page] = True

    return page_faults

def lfu_replacement(pages: List[int], frames: int) -> int:
    memory = set()
    frequency = defaultdict(int)
    usage_order = OrderedDict()
    page_faults = 0

    for i, page in enumerate(pages):
        if page in memory:
            frequency[page] += 1
            usage_order.move_to_end(page)
            continue

        page_faults += 1
        if len(memory) >= frames:
            min_freq = min(frequency[p] for p in memory)
            candidates = [p for p in memory if frequency[p] == min_freq]
            to_remove = next(p for p in usage_order if p in candidates)
            
            memory.remove(to_remove)
            del frequency[to_remove]
            del usage_order[to_remove]

        memory.add(page)
        frequency[page] = 1
        usage_order[page] = True

    return page_faults

def optimal_replacement(pages: List[int], frames: int) -> int:
    memory = set()
    page_faults = 0

    for i, page in enumerate(pages):
        if page in memory:
            continue

        page_faults += 1
        if len(memory) >= frames:
            # Find page not used for longest time in future
            farthest = -1
            to_replace = None
            
            for p in memory:
                try:
                    next_use = pages.index(p, i+1)
                except ValueError:
                    to_replace = p
                    break
                    
                if next_use > farthest:
                    farthest = next_use
                    to_replace = p

            memory.remove(to_replace)

        memory.add(page)

    return page_faults

@app.post("/simulate")
async def run_simulation(request: Request) -> List[Dict]:
    data = await request.json()
    
    try:
        # Required parameters
        total_virtual_pages = int(data["total_virtual_pages"])
        total_physical_frames = int(data["total_physical_frames"])
        tlb_size = int(data["tlb_size"])
        
        # Check if custom memory requests are provided
        if "memory_requests" in data and data["memory_requests"]:
            memory_requests = parse_memory_requests(data["memory_requests"])
            total_access_requests = len(memory_requests)
        else:
            total_access_requests = int(data["total_access_requests"])
            memory_requests = generate_memory_requests(total_access_requests, total_virtual_pages)
        
        # Force single-level paging for now
        page_table_type = "single"
        replacement_algo = data.get("replacement_algo", "fifo").lower()
        
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail="Invalid input parameters")

    results = []
    paging = SingleLevelPaging(total_physical_frames)
    tlb_hits = tlb_misses = 0
    tlb_cache = OrderedDict()
    
    # Run simulation
    for page in memory_requests:
        if page in tlb_cache:
            tlb_hits += 1
            tlb_cache.move_to_end(page)
        else:
            tlb_misses += 1
            paging.access_page(page)
            if len(tlb_cache) >= tlb_size:
                tlb_cache.popitem(last=False)
            tlb_cache[page] = True
    
    # Test each algorithm
    replacement_algos = {
        "fifo": fifo_replacement,
        "lru": lru_replacement,
        "lfu": lfu_replacement,
        "optimal": optimal_replacement
    }
    
    if replacement_algo == "all":
        selected_algorithms = replacement_algos.items()
    else:
        selected_algorithms = [(replacement_algo, replacement_algos[replacement_algo])]
    
    for algo, func in selected_algorithms:
        replacement_faults = func(memory_requests, total_physical_frames)
        
        results.append({
            "paging_type": "SINGLE",
            "algorithm": algo.upper(),
            "total_page_faults": paging.page_faults,
            "tlb_hits": tlb_hits,
            "tlb_misses": tlb_misses,
            "page_fault_rate": round(paging.page_faults / total_access_requests, 2),
            "tlb_hit_ratio": round(tlb_hits / total_access_requests, 2),
            "faults": replacement_faults
        })
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)