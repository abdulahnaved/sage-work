# SageMath Auto-Grader

This repository provides a simple framework for grading student SageMath notebooks (.ipynb) using *Docker*.

## Why Docker?
- Installing SageMath locally (especially on Windows) is large and complicated.  
- With Docker, everyone runs the same prebuilt environment: no setup problems.  
- Works the same on Windows, Mac, and Linux.

---

## Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed  
- Git installed (to clone this repo)

---

## Setup
Clone the repository:
```bash
git clone https://github.com/<your-username>/sage-grader.git
cd sage-grader
