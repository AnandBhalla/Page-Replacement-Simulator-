class PageReplacementSimulator:
    def __init__(self):
        self.page_table = {}
        self.memory = []
        self.stats = {'hits': 0, 'faults': 0, 'total': 0}
        self.history = []
    
    def initialize_system(self, frame_count):
        """Initialize the system with empty memory frames"""
        self.memory = [None] * frame_count
        self.page_table = {}
        self.stats = {'hits': 0, 'faults': 0, 'total': 0}
        self.history = []
    
    def check_page_in_memory(self, page):
        """Check if page exists in physical memory"""
        return page in self.memory
    
    def load_page(self, page, index):
        """Load page into specific memory frame"""
        self.memory[index] = page
        self.page_table[page] = {'frame': index, 'loaded_at': self.stats['total']}
    
    def update_page_table(self, page, frame=None):
        """Update page table metadata"""
        if frame is not None:
            self.page_table[page] = {'frame': frame, 'loaded_at': self.stats['total']}
        else:
            self.page_table[page]['last_used'] = self.stats['total']
    
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
                if algorithm == 'LRU':
                    self.update_page_table(page)
                self.history.append({'page': page, 'memory': list(self.memory), 'event': 'hit'})
            else:
                self.record_fault()
                if None in self.memory:
                    # Empty frame available
                    frame_index = self.memory.index(None)
                    self.load_page(page, frame_index)
                else:
                    # Page replacement needed
                    if algorithm == 'FIFO':
                        victim_page = self.handle_fifo()
                    elif algorithm == 'LRU':
                        victim_page = self.handle_lru()
                    elif algorithm == 'OPTIMAL':
                        victim_page = self.handle_optimal(reference_string[i+1:])
                    
                    frame_index = self.page_table[victim_page]['frame']
                    del self.page_table[victim_page]
                    self.load_page(page, frame_index)
                
                self.history.append({'page': page, 'memory': list(self.memory), 'event': 'fault'})
        
        return self.calculate_ratios()
    
    def handle_fifo(self):
        """FIFO page replacement implementation"""
        oldest_page = None
        oldest_time = float('inf')
        
        for page, data in self.page_table.items():
            if data['loaded_at'] < oldest_time:
                oldest_time = data['loaded_at']
                oldest_page = page
        
        return oldest_page
    
    def handle_lru(self):
        """LRU page replacement implementation"""
        least_recent_page = None
        least_recent_time = float('inf')
        
        for page, data in self.page_table.items():
            last_used = data.get('last_used', data['loaded_at'])
            if last_used < least_recent_time:
                least_recent_time = last_used
                least_recent_page = page
        
        return least_recent_page
    
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
        
        return farthest_page if farthest_page is not None else list(self.page_table.keys())[0]
    
    def print_step_by_step(self):
        """Print step-by-step simulation results"""
        print("\nStep-by-Step Simulation Results:")
        print("Page | Memory State | Event")
        print("-----------------------------")
        for step in self.history:
            print(f"{step['page']:4} | {str(step['memory']):12} | {step['event']}")
    
    def generate_report(self):
        """Generate final simulation report"""
        ratios = self.calculate_ratios()
        report = {
            'total_references': self.stats['total'],
            'page_hits': self.stats['hits'],
            'page_faults': self.stats['faults'],
            'hit_ratio': ratios['hit_ratio'],
            'fault_ratio': ratios['fault_ratio'],
            'final_memory_state': list(self.memory)
        }
        return report
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
        algo_choice = input("Select algorithm (1-3): ")
        if algo_choice == '1':
            algorithm = 'FIFO'
            break
        elif algo_choice == '2':
            algorithm = 'LRU'
            break
        elif algo_choice == '3':
            algorithm = 'OPTIMAL'
            break
        print("Invalid choice! Please select 1-3.")
    
    # Run simulation
    print("\n" + "="*50)
    print(f"RUNNING {algorithm} ALGORITHM SIMULATION")
    print("="*50)
    
    ratios = simulator.simulate(ref_string, frames, algorithm)
    
    # Display detailed step-by-step results
    print("\n" + "-"*60)
    print("STEP-BY-STEP SIMULATION DETAILS:")
    print("-"*60)
    print(f"{'Step':<5} | {'Page':<5} | {'Memory State':<20} | {'Event':<15} | {'Action':<20}")
    print("-"*60)
    
    for i, step in enumerate(simulator.history, 1):
        action = ""
        if step['event'] == 'fault':
            if None in step['memory']:
                action = "Loaded to empty frame"
            else:
                # Find which page was replaced
                prev_step = simulator.history[i-2]['memory'] if i > 1 else [None]*frames
                replaced = set(prev_step) - set(step['memory'])
                if replaced:
                    action = f"Replaced page {replaced.pop()}"
        
        print(f"{i:<5} | {step['page']:<5} | {str(step['memory']):<20} | {step['event'].upper():<15} | {action:<20}")
    
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
    print(f"{'Hit Ratio':<20}: {report['hit_ratio']:.2%}")
    print(f"{'Fault Ratio':<20}: {report['fault_ratio']:.2%}")
    print("-"*40)
    print(f"{'Final Memory State':<20}: {report['final_memory_state']}")
    print("\nSimulation Complete!")