# Page Table (Virtual Page -> Physical Frame Mapping)
page_table = {0: 5, 1: 3, 2: 8, 3: 6}  # Example Mapping
PAGE_SIZE = 1024  # Assume 1KB Pages

def translate_address(virtual_address):
    page_number = virtual_address // PAGE_SIZE
    offset = virtual_address % PAGE_SIZE

    if page_number in page_table:
        frame_number = page_table[page_number]
        physical_address = (frame_number * PAGE_SIZE) + offset
        return f"Physical Address: {physical_address}"
    else:
        return "Page Fault! Page not in memory."

# Example: Translate virtual address 2050
print(translate_address(2050))  # Output: Physical Address: 5122

from collections import deque

def fifo_page_replacement(pages, frames):
    memory = deque()  # Queue to hold pages in memory
    page_faults = 0

    for page in pages:
        if page not in memory:
            if len(memory) >= frames:
                memory.popleft()  # Remove oldest page
            memory.append(page)
            page_faults += 1
        print(f"Memory: {list(memory)}")

    return f"Total Page Faults: {page_faults}"

# Example: Pages to be accessed and Frame Size = 3
pages = [1, 3, 0, 3, 5, 6, 3]
frames = 3
print(fifo_page_replacement(pages, frames))