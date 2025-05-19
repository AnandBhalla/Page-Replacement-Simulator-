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


![Screenshot 2025-05-19 210021](https://github.com/user-attachments/assets/35e9a320-6597-4e05-8467-6ce858c2ae99)
![Screenshot 2025-05-19 210101](https://github.com/user-attachments/assets/19cbd051-4cf6-4b7e-8b8d-ba68d11147f8)
![Screenshot 2025-05-19 210121](https://github.com/user-attachments/assets/cf1b99c8-ad3c-4e8c-9b7c-d683e7ca1c05)
![Screenshot 2025-05-19 210131](https://github.com/user-attachments/assets/8fec0aca-79e3-4355-84b3-205dfbe1f817)
![Screenshot 2025-05-19 210155](https://github.com/user-attachments/assets/91a742a2-b873-436d-b4bf-ded6dc5fa1ec)
![Screenshot 2025-05-19 210215](https://github.com/user-attachments/assets/b90c32f0-4864-4dbd-bd69-dd9c7691aa75)
![Screenshot 2025-05-19 210227](https://github.com/user-attachments/assets/e597e8be-b89f-45dd-93fe-3acf12a2667b)


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

