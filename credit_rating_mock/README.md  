## Installation and Steps to run the code
1. Clone the Repository
   git clone git@github.com:Suri321123/CredRater.git
2. Create Virtual Environment
    python3 -m venv venv
    source venv/bin/activate
3. Install Requirements
    pip install -r requirement.txt
4. Run pytest
    pytest -v
5. Run core logic
    cd credit_rating_mock
    python credit_rating.py 
6. Expected Output
    Mortgage 1: Final Credit Rating = AAA
    Mortgage 2: Final Credit Rating = BBB

Technical decisions made:
    1. used OOPs aproach to make the code more scalable 
    2. Class based approach made clean separation of logic 
    3. Made each class independently testable
    4. Used some design patterns top make the code more decoupled. and followed the SOLID principle.

Optional Enhancements:
1. Performance Optimization: 
    For large data set we can use multiprocessing or threading or asyncio to process the the mortages asyncronously.
    We can keep the rules in cache, so that we do not have to fetch it from db every time
2. Error Handling: 
    Handled using try except, we can further use decorators patterns to log the errors on some logging tool available online.
