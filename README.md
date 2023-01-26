# MPCS 51220 Homework G-01

## Team: 404 Team Not Found
**Updated**: 28 April 2022<br>
**Version**: v1_0

# Team Members and Work Delegation
The whole team worked in smaller groups with seperate responsibilities, as follows: <br>
**Back End**<br>
Hanze Hu, hanzeh@uchicago.edu <br>
Yusen Zhang, yusen@uchicago.edu

**Front End**<br>
Prajval Mohan, prajvalmohan@uchicago.edu<br>
Thanushri Rajmohan, thanushrir@uchicago.edu

**Testing**<br>
Hayder Saad, haydersaad@uchicago.edu

# Specifications
See Specifications for this project at https://canvas.uchicago.edu/courses/42548/assignments/456278

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

# E grade requirement
1. Implemented all requirements from A-01 including all special requirements.
2. Implemented persistence mechanism in such a way as to not generate loss of work, change is made to the data file as soon as requests are received on the API endpoints.
3. The UI is very user friendly and We limited the number of results demonstrated so as to avoid overwhelming users.
4. Besides basic tests to show that our API works, we also test error handling ability of our server.
5. No apparent code smell.
6. We follow coding style guide totally.
7. We streamline the seed data handling by providing reset.py


# Jira Usage Discussion
A system like JIRA could help organize the group's work in a few meaningful ways:
1. Jira could be used to delegate not just work but also responsibility. For example, each new feature could be assigned to one group member and they will be responsible for making sure it is implemented correctly and in a timely manner.
2. Jira could be used to approximate how long the project will take. Since most/all of the features that are required to be implemented could be given an approximate time, it could give the group a better sense of the overall project and ensure that the project is on track to finish on time.
3. Jira could be used to track priorities of different features. This was especially important because we noticed that in our case, the implementation of the client end is somewhat dependent on the implemntation of the server, since the API endpoints and formats must be confirmed before the client side could implement it. Using Jira could set dependencies and we can better manage the group's time (e.g. making sure the server is completed by Wednesday so the front end group could finish by Friday), and these timelines would be easily tracked using Jira.