from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from collections import defaultdict

app = FastAPI()

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    requests: List[int]
    frames: int
    algorithm: str

class PageReplacementSimulator:
    def __init__(self):
        self.page_table = {}
        self.memory = []
        self.stats = {'hits': 0, 'faults': 0, 'total': 0}
        self.history = []
        self.access_counts = defaultdict(int)  # For LFU/MFU
        self.page_faults = 0
    
    def initialize_system(self, frame_count):
        """Initialize the system with empty memory frames"""
        self.memory = [None] * frame_count
        self.page_table = {}
        self.stats = {'hits': 0, 'faults': 0, 'total': 0}
        self.history = []
        self.access_counts = defaultdict(int)
        self.page_faults = 0
    
    def check_page_in_memory(self, page):
        """Check if page exists in physical memory"""
        return page in self.memory
    
    def load_page(self, page, index):
        """Load page into specific memory frame"""
        self.memory[index] = page
        self.page_table[page] = {
            'frame': index,
            'loaded_at': self.stats['total'],
            'last_used': self.stats['total']
        }
        self.access_counts[page] += 1
    
    def update_page_table(self, page, frame=None):
        """Update page table metadata"""
        if frame is not None:
            self.page_table[page] = {
                'frame': frame,
                'loaded_at': self.stats['total'],
                'last_used': self.stats['total']
            }
            self.access_counts[page] += 1
        else:
            self.page_table[page]['last_used'] = self.stats['total']
            self.access_counts[page] += 1
    
    def record_hit(self):
        """Record a page hit"""
        self.stats['hits'] += 1
        self.stats['total'] += 1
    
    def record_fault(self):
        """Record a page fault"""
        self.stats['faults'] += 1
        self.stats['total'] += 1
        self.page_faults += 1
    
    def calculate_ratios(self):
        """Calculate hit and fault ratios"""
        return {
            'hit_ratio': self.stats['hits'] / self.stats['total'] if self.stats['total'] > 0 else 0,
            'fault_ratio': self.stats['faults'] / self.stats['total'] if self.stats['total'] > 0 else 0
        }
    
    def simulate(self, reference_string, frame_count, algorithm):
        """Main simulation function"""
        self.initialize_system(frame_count)
        
        for i, page in enumerate(reference_string):
            if self.check_page_in_memory(page):
                self.record_hit()
                if algorithm in ['LRU', 'MRU']:
                    self.update_page_table(page)
                self.history.append({
                    'page': page,
                    'memory': list(self.memory),
                    'event': 'hit',
                    'action': ''
                })
            else:
                self.record_fault()
                if None in self.memory:
                    frame_index = self.memory.index(None)
                    self.load_page(page, frame_index)
                    action = f"Loaded to frame {frame_index}"
                else:
                    if algorithm == 'FIFO':
                        victim_page = self.handle_fifo()
                    elif algorithm == 'LRU':
                        victim_page = self.handle_lru()
                    elif algorithm == 'OPTIMAL':
                        victim_page = self.handle_optimal(reference_string[i+1:])
                    elif algorithm == 'LFU':
                        victim_page = self.handle_lfu()
                    elif algorithm == 'MRU':
                        victim_page = self.handle_mru()
                    elif algorithm == 'MFU':
                        victim_page = self.handle_mfu()
                    
                    frame_index = self.page_table[victim_page]['frame']
                    action = f"Replaced page {victim_page} (frame {frame_index})"
                    del self.page_table[victim_page]
                    self.load_page(page, frame_index)
                
                self.history.append({
                    'page': page,
                    'memory': list(self.memory),
                    'event': 'fault',
                    'action': action
                })
        
        return self.calculate_ratios()
    
    def handle_fifo(self):
        """FIFO page replacement implementation"""
        oldest_page = min(self.page_table.items(), key=lambda x: x[1]['loaded_at'])[0]
        return oldest_page
    
    def handle_lru(self):
        """LRU page replacement implementation"""
        least_recent = min(self.page_table.items(), key=lambda x: x[1]['last_used'])[0]
        return least_recent
    
    def handle_optimal(self, future_references):
        """Optimal page replacement implementation"""
        farthest_page = None
        farthest_index = -1
        
        for page in self.page_table:
            try:
                next_use = future_references.index(page)
            except ValueError:
                return page  # This page won't be used again
            
            if next_use > farthest_index:
                farthest_index = next_use
                farthest_page = page
        
        return farthest_page if farthest_page else next(iter(self.page_table))
    
    def handle_lfu(self):
        """Least Frequently Used implementation"""
        # Get all pages with minimum count
        min_count = min(self.access_counts[p] for p in self.memory if p is not None)
        candidates = [p for p in self.memory if p is not None and self.access_counts[p] == min_count]
        
        # If tie, use LRU as tiebreaker
        if len(candidates) > 1:
            return min(candidates, key=lambda p: self.page_table[p]['last_used'])
        return candidates[0]
    
    def handle_mru(self):
        """Most Recently Used implementation"""
        most_recent = max(self.page_table.items(), key=lambda x: x[1]['last_used'])[0]
        return most_recent
    
    def handle_mfu(self):
        """Most Frequently Used implementation"""
        # Get all pages with maximum count
        max_count = max(self.access_counts[p] for p in self.memory if p is not None)
        candidates = [p for p in self.memory if p is not None and self.access_counts[p] == max_count]
        
        # If tie, use LRU as tiebreaker
        if len(candidates) > 1:
            return min(candidates, key=lambda p: self.page_table[p]['last_used'])
        return candidates[0]

@app.post("/simulate")
async def run_simulation(request: SimulationRequest):
    simulator = PageReplacementSimulator()
    
    # Validate algorithm
    valid_algorithms = ['FIFO', 'LRU', 'OPTIMAL', 'LFU', 'MRU', 'MFU']
    if request.algorithm.upper() not in valid_algorithms:
        return {"error": "Invalid algorithm. Choose from FIFO, LRU, OPTIMAL, LFU, MRU, or MFU."}
    
    # Run simulation
    ratios = simulator.simulate(request.requests, request.frames, request.algorithm.upper())
    tlb_hits = simulator.stats['hits']
    
    # Prepare response
    response = [{
        "paging_type": "SINGLE",
        "algorithm": request.algorithm.upper(),
        "total_page_faults": simulator.page_faults,
        "total_hits": tlb_hits,
    }]
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
