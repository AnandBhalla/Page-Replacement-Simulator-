from fastapi import FastAPI
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
        self.access_counts = defaultdict(int)
        self.page_faults = 0
        self.page_table_history = []
    
    def initialize_system(self, frame_count):
        self.memory = [None] * frame_count
        self.page_table = {}
        self.stats = {'hits': 0, 'faults': 0, 'total': 0}
        self.history = []
        self.access_counts = defaultdict(int)
        self.page_faults = 0
        self.page_table_history = []
    
    def check_page_in_memory(self, page):
        return page in self.memory
    
    def load_page(self, page, index):
        self.memory[index] = page
        self.page_table[page] = {
            'frame': index,
            'loaded_at': self.stats['total'],
            'last_used': self.stats['total']
        }
        self.access_counts[page] += 1
    
    def update_page_table(self, page, frame=None):
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
        self.stats['hits'] += 1
        self.stats['total'] += 1
    
    def record_fault(self):
        self.stats['faults'] += 1
        self.stats['total'] += 1
        self.page_faults += 1
    
    def calculate_ratios(self):
        return {
            'hit_ratio': self.stats['hits'] / self.stats['total'] if self.stats['total'] > 0 else 0,
            'fault_ratio': self.stats['faults'] / self.stats['total'] if self.stats['total'] > 0 else 0
        }
    
    def simulate(self, reference_string, frame_count, algorithm):
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
                    'action': '',
                    'step': i + 1
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
                    'action': action,
                    'step': i + 1
                })
            
            # Record memory state at each step
            self.page_table_history.append(list(self.memory))
        
        return {
            'algorithm': algorithm,
            'total_page_faults': self.page_faults,
            'total_hits': self.stats['hits'],
            'hit_ratio': self.calculate_ratios()['hit_ratio'],
            'fault_ratio': self.calculate_ratios()['fault_ratio'],
            'history': self.history,
            'page_table': self.page_table_history,
            'final_memory_state': list(self.memory) if self.memory else []
        }
    
    def handle_fifo(self):
        oldest_page = min(self.page_table.items(), key=lambda x: x[1]['loaded_at'])[0]
        return oldest_page
    
    def handle_lru(self):
        least_recent = min(self.page_table.items(), key=lambda x: x[1]['last_used'])[0]
        return least_recent
    
    def handle_optimal(self, future_references):
        farthest_page = None
        farthest_index = -1
        
        for page in self.page_table:
            try:
                next_use = future_references.index(page)
            except ValueError:
                return page
            
            if next_use > farthest_index:
                farthest_index = next_use
                farthest_page = page
        
        return farthest_page if farthest_page else next(iter(self.page_table))
    
    def handle_lfu(self):
        min_count = min(self.access_counts[p] for p in self.memory if p is not None)
        candidates = [p for p in self.memory if p is not None and self.access_counts[p] == min_count]
        
        if len(candidates) > 1:
            return min(candidates, key=lambda p: self.page_table[p]['last_used'])
        return candidates[0]
    
    def handle_mru(self):
        most_recent = max(self.page_table.items(), key=lambda x: x[1]['last_used'])[0]
        return most_recent
    
    def handle_mfu(self):
        max_count = max(self.access_counts[p] for p in self.memory if p is not None)
        candidates = [p for p in self.memory if p is not None and self.access_counts[p] == max_count]
        
        if len(candidates) > 1:
            return min(candidates, key=lambda p: self.page_table[p]['last_used'])
        return candidates[0]

@app.post("/simulate")
async def run_simulation(request: SimulationRequest):
    simulator = PageReplacementSimulator()
    
    valid_algorithms = ['FIFO', 'LRU', 'OPTIMAL', 'LFU', 'MRU', 'MFU', 'ALL']
    if request.algorithm.upper() not in valid_algorithms:
        return {"error": "Invalid algorithm. Choose from FIFO, LRU, OPTIMAL, LFU, MRU, MFU, or ALL."}
    
    response = []
    
    if request.algorithm.upper() == 'ALL':
        algorithms = ['FIFO', 'LRU', 'OPTIMAL', 'LFU', 'MRU', 'MFU']
        for algo in algorithms:
            result = simulator.simulate(request.requests, request.frames, algo)
            response.append({
                "paging_type": "SINGLE",
                "algorithm": algo,
                "total_page_faults": result['total_page_faults'],
                "total_hits": result['total_hits'],
                "hit_ratio": result['hit_ratio'],
                "fault_ratio": result['fault_ratio'],
                "history": result['history'],
                "page_table": result['page_table'],
                "final_memory_state": result['final_memory_state']
            })
        
    else:
        result = simulator.simulate(request.requests, request.frames, request.algorithm.upper())
        
        response.append({
            "paging_type": "SINGLE",
            "algorithm": request.algorithm.upper(),
            "total_page_faults": result['total_page_faults'],
            "total_hits": result['total_hits'],
            "hit_ratio": result['hit_ratio'],
            "fault_ratio": result['fault_ratio'],
            "history": result['history'],
            "page_table": result['page_table'],
            "final_memory_state": result['final_memory_state']
        })
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)