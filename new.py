def calculate_tlb_stats(pages, tlb_size):
    tlb_cache = set()
    tlb_order = []
    hits = 0
    misses = 0
    
    for page in pages:
        if page in tlb_cache:
            hits += 1
            tlb_order.remove(page)
            tlb_order.append(page)
        else:
            misses += 1
            if len(tlb_cache) >= tlb_size:
                evicted = tlb_order.pop(0)
                tlb_cache.remove(evicted)
            tlb_cache.add(page)
            tlb_order.append(page)
    
    hit_ratio = hits / (hits + misses) if (hits + misses) > 0 else 0
    return {
        "TLB Hits": hits,
        "TLB Misses": misses,
        "TLB Hit Ratio": f"{hit_ratio:.2f}"
    }

def lru_page_replacement(pages, capacity):
    memory = set()
    last_used = {}
    page_faults = 0
    fault_sequence = []
    
    for i, page in enumerate(pages):
        if page in memory:
            fault_sequence.append(0)
            last_used[page] = i
        else:
            page_faults += 1
            fault_sequence.append(1)
            if len(memory) >= capacity:
                lru_page = min(memory, key=lambda p: last_used[p])
                memory.remove(lru_page)
            memory.add(page)
            last_used[page] = i
    
    fault_rate = page_faults / len(pages)
    return {
        'total_page_faults': page_faults,
        'fault_sequence': fault_sequence,
        'fault_rate': round(fault_rate, 3),
        'hit_count': len(pages) - page_faults,
        'hit_rate': round(1 - fault_rate, 3),
        'final_memory_state': list(memory)
    }

# Proper input processing
if __name__ == "__main__":
    pages_input = input("Enter page requests (comma-separated): ")
    pages = list(map(int, pages_input.split(',')))  # Proper conversion
    
    tlb_size = int(input("Enter TLB size: "))
    capacity = int(input("Enter memory capacity: "))
    
    tlb_results = calculate_tlb_stats(pages, tlb_size)
    print("\n===== TLB Results =====")
    print(f"TLB Hits: {tlb_results['TLB Hits']}")
    print(f"TLB Misses: {tlb_results['TLB Misses']}")
    print(f"TLB Hit Ratio: {tlb_results['TLB Hit Ratio']}")
    
    lru_results = lru_page_replacement(pages, capacity)
    print("\n===== LRU Page Replacement Results =====")
    print(f"Total Page Faults: {lru_results['total_page_faults']}")
    print(f"Fault Sequence: {lru_results['fault_sequence']}")
    print(f"Fault Rate: {lru_results['fault_rate']:.1%}")
    print(f"Hit Count: {lru_results['hit_count']}")
    print(f"Hit Rate: {lru_results['hit_rate']:.1%}")
    print(f"Final Memory State: {lru_results['final_memory_state']}")