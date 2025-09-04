# NFA Project
This project is a backend application for NFA.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+

### Setup & Run
1. Clone the repository:
   ```bash
   git clone https://github.com/smsibghatullah/nfa_backend
   cd nfa_backend
   ```
2. Build and start the containers:
   ```bash
   make up
   ```

3. To stop the containers:
   ```bash
   make down
   ```

4. To stop the containers with deleting contaiers:
   ```bash
   make down-v
   ```

5. To see the runing containers:
   ```bash
   make ps
   ```

5. Access the admin dashboard at `http://167.71.230.14:8080/admin/`

## Development
- Source code is in `src/nfa/`
- Static files are in `src/nfa/static/`