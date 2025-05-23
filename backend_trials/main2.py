from collections import defaultdict

class PageReplacementSimulator:
    def __init__(self):
        self.page_table = {}
        self.memory = []
        self.stats = {'hits': 0, 'faults': 0, 'total': 0}
        self.history = []
        self.access_counts = defaultdict(int)  # For LFU/MFU
    
    def initialize_system(self, frame_count):
        """Initialize the system with empty memory frames"""
        self.memory = [None] * frame_count
        self.page_table = {}
        self.stats = {'hits': 0, 'faults': 0, 'total': 0}
        self.history = []
        self.access_counts = defaultdict(int)
    
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
    
    def print_step_by_step(self):
        """Print step-by-step simulation results"""
        print("\nStep-by-Step Simulation:")
        print(f"{'Step':<5} | {'Page':<5} | {'Memory':<20} | {'Event':<7} | {'Action':<30}")
        print("-" * 70)
        for i, step in enumerate(self.history, 1):
            print(f"{i:<5} | {step['page']:<5} | {str(step['memory']):<20} | {step['event'].upper():<7} | {step['action']:<30}")
    
    def generate_report(self):
        """Generate final simulation report"""
        ratios = self.calculate_ratios()
        return {
            'total_references': self.stats['total'],
            'page_hits': self.stats['hits'],
            'page_faults': self.stats['faults'],
            'hit_ratio': f"{ratios['hit_ratio']:.2%}",
            'fault_ratio': f"{ratios['fault_ratio']:.2%}",
            'final_memory_state': list(self.memory)
        }

# Example Usage
if __name__ == "__main__":
    simulator = PageReplacementSimulator()
    
    print("\n" + "="*50)
    print("PAGE REPLACEMENT ALGORITHM SIMULATOR")
    print("="*50)
    
    # Get user inputs
    while True:
        ref_str = input("\nEnter page reference sequence (comma or space separated): ")
        try:
            ref_string = [int(x) for x in ref_str.replace(',', ' ').split()]
            break
        except ValueError:
            print("Invalid input! Please enter numbers only.")
    
    while True:
        frames = input("Enter number of memory frames: ")
        if frames.isdigit() and int(frames) > 0:
            frames = int(frames)
            break
        print("Invalid input! Please enter a positive integer.")
    
    while True:
        print("\nAvailable algorithms:")
        print("1. FIFO (First-In-First-Out)")
        print("2. LRU (Least Recently Used)")
        print("3. OPTIMAL (Optimal Replacement)")
        print("4. LFU (Least Frequently Used)")
        print("5. MRU (Most Recently Used)")
        print("6. MFU (Most Frequently Used)")
        algo_choice = input("Select algorithm (1-6): ")
        if algo_choice == '1':
            algorithm = 'FIFO'
            break
        elif algo_choice == '2':
            algorithm = 'LRU'
            break
        elif algo_choice == '3':
            algorithm = 'OPTIMAL'
            break
        elif algo_choice == '4':
            algorithm = 'LFU'
            break
        elif algo_choice == '5':
            algorithm = 'MRU'
            break
        elif algo_choice == '6':
            algorithm = 'MFU'
            break
        print("Invalid choice! Please select 1-6.")
    
    # Run simulation
    print("\n" + "="*50)
    print(f"RUNNING {algorithm} ALGORITHM SIMULATION")
    print("="*50)
    
    ratios = simulator.simulate(ref_string, frames, algorithm)
    
    # Display detailed step-by-step results
    simulator.print_step_by_step()
    
    # Display final report
    report = simulator.generate_report()
    
    print("\n" + "="*50)
    print("FINAL SIMULATION REPORT")
    print("="*50)
    print(f"\nAlgorithm Used: {algorithm}")
    print(f"Reference String: {ref_string}")
    print(f"Number of Frames: {frames}\n")
    
    print("-"*40)
    print(f"{'Total References':<20}: {report['total_references']}")
    print(f"{'Page Hits':<20}: {report['page_hits']}")
    print(f"{'Page Faults':<20}: {report['page_faults']}")
    print("-"*40)
    print(f"{'Hit Ratio':<20}: {report['hit_ratio']}")
    print(f"{'Fault Ratio':<20}: {report['fault_ratio']}")
    print("-"*40)
    print(f"{'Final Memory State':<20}: {report['final_memory_state']}")
    print("\nSimulation Complete!")