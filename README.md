🧠 Page Replacement Simulator
A simulation tool for understanding how paging works in memory management, including main memory and cache. This project visually demonstrates various page replacement algorithms like FIFO, LRU, etc., making it easier for students and developers to grasp the concept of virtual memory and page faults.

🚀 Tech Stack
Frontend: React.js 

Backend: Python

🎨 Frontend
The frontend provides a user-friendly interface to simulate and visualize memory operations:

Input: Number of frames, reference string, and algorithm type (FIFO, LRU, etc.)

Output: Table/grid showing page hits, page faults, memory state

Interactive visualizations (step-by-step simulation)

Clear display of stats: total hits, faults, fault rate

✅Features

Dropdown to select page replacement algorithm

Text field for reference string input

Dynamic rendering of memory blocks

Color-coded indicators for page hits and faults

Responsive layout for desktop and mobile

🛠️ Backend

The backend  handles the logic and processing:

Accepts reference strings and config via API

Runs selected page replacement algorithm (FIFO, LRU, etc.)

Returns step-by-step memory state updates

📸 Demo Screenshots

![Screenshot 2025-03-28 162032](https://github.com/user-attachments/assets/7c10d310-0add-4d45-af46-275bb5e1155e)
![Screenshot 2025-04-03 192201](https://github.com/user-attachments/assets/9bc9e091-59c5-433a-89c1-3fca9ff88fa2)
![Screenshot 2025-03-28 150637](https://github.com/user-attachments/assets/b99177a0-0c3d-4563-a80d-266bbdcf773a)

🧠 Algorithms Included

First-In-First-Out (FIFO)

Least Recently Used (LRU)

Most Recently Used (MRU)

Least Frequently Used (LFU)

Most Frequently Used (MFU)

Optimal Page Replacement (OPT)

📝 Todo
Export results to CSV

Implement different types of Page Tables

Add animations or step-by-step simulation controls

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first.

