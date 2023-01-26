# Workshop Facilities Reservation System

**Updated**: 28 April 2022<br>
**Version**: v1_0

# Specifications
<br> 
A FastAPI application that provides the functionality of the reservation system through a (pragmatic) RESTful API.
The system pre-loads a representative set of data to streamline manual testing and demonstration.
The system adopts a file based persistence mechanism.
The system adopted Test Driven Development using pytest that involved testing the API endpoints.
Scope control implementation was carried out.
A console client allows a user to interact with the API to perform the reservation system functions.
Basic API documentation for the system exists as well.
<br> 

# Special Requirements
<br> 
Streamlining the seed data handling in the system by providing reset.py. 
Robust job implementing the server tests and the client side tests.

# System Instructions
## Server
**Documentations**: `http://127.0.0.1:800/v1_0/docs <br>
The preset data file could loaded by running the python file within the server subdirectory:
```
cd server
python tests/reset.py
```
The server should be run with uvicorn in the following style:
```
cd server
uvicorn web:app --reload
```

## Client
The client side program could be run by running the front.py file in the client directory
```
cd client
python front.py
```

## Testing
```
cd server
python tests/reset.py
pytest
```

# Simplifications
1. The system does not check for the uniqueness of a given user id, in our implementation we have assumed that the ID is unique.

# Version Control Scope
## Git Branches
- master
- dev
- feature

## Git Commit and Branching Policy
- All new features should be implemented in a seperate feature branch
- All commits should have a clear, relevant description of what was implemented in that commit
- Once a feature has been completed, and there's no remaining conflict, the branch should be merged onto _dev_ by the author of the branch

# Jira Usage Discussion
A system like JIRA could help organize the work in a few meaningful ways:
1. Jira could be used to delegate not just work but also responsibility. For example, each new feature could be assigned to a member and they will be responsible for making sure it is implemented correctly and in a timely manner.
2. Jira could be used to approximate how long the project will take. Since most/all of the features that are required to be implemented could be given an approximate time, it could give the group a better sense of the overall project and ensure that the project is on track to finish on time.
3. Jira could be used to track priorities of different features. This was especially important because in the case of this project, the implementation of the client end is somewhat dependent on the implementation of the server, since the API endpoints and formats must be confirmed before the client side could implement it. Using Jira could set dependencies and we can better manage the group's time (e.g. making sure the server is completed by Wednesday so the front end group could finish by Friday), and these timelines would be easily tracked using Jira.
