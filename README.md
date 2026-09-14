# StudyFlow

Developer: Rauhan Aziz ([Azizr96](https://www.github.com/Azizr96))

[![GitHub commit activity](https://img.shields.io/github/commit-activity/t/Azizr96/studyflow)](https://www.github.com/Azizr96/studyflow/commits/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/Azizr96/studyflow)](https://www.github.com/Azizr96/studyflow/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/Azizr96/studyflow)](https://www.github.com/Azizr96/studyflow)
[![Heroku Deployment](https://img.shields.io/badge/deployment-Heroku-purple)](https://studyflow-83c0183db652.herokuapp.com)

![StudyFlow responsive mockup](documentation/mockup1.png)
![StudyFlow responsive mockup](documentation/)


## Project Introduction and Rationale

StudyFlow is a fictional Clinical Trial Site Management System developed to provide a centralised platform for managing key activities associated with clinical research studies. The application allows authorised users to manage studies, fictional participants, scheduled visits, study documents, user assignments and notifications from a single responsive interface.

Clinical trial sites can involve multiple studies, participants, visits, documents and members of staff at the same time. Keeping this information organised and ensuring that users only have access to information relevant to their responsibilities is therefore an important part of site management. StudyFlow was designed around this problem by providing structured study management alongside role-based access control.

The application supports two main levels of access. Elevated users, such as Administrators, Investigators and Project Leads, can create studies, manage users, approve registrations and assign users to studies. Standard users, such as Study Coordinators and Trial Assistants, can access studies assigned to them and manage the fictional participants, visits and study documents associated with those studies.

I chose to develop StudyFlow because of my professional background in pharmaceutical research and clinical trials. This gave me familiarity with the workflows and organisational challenges involved in clinical research and allowed me to apply existing domain knowledge to a full-stack software development project. Rather than creating a generic CRUD application, I wanted to build a system based on a realistic professional scenario while demonstrating the technical skills developed during the Full Stack Software Development course.

StudyFlow is an educational portfolio project and is not intended for use with real clinical trial or patient data. All participant information used within the application is fictional.

The project was developed using Django and Python for the back end, PostgreSQL for relational data storage, HTML, CSS and Bootstrap for the responsive front end, Cloudinary for uploaded study documents, and WhiteNoise for static file handling. The application is deployed through Heroku.

The main goals of StudyFlow are to:

- provide a clear central location for clinical study information;
- implement secure authentication and role-based permissions;
- allow authorised users to manage fictional participants and study visits;
- allow study documents to be uploaded and associated with the appropriate study;
- provide relevant notifications about study activity;
- restrict standard users to studies to which they have been assigned;
- provide a responsive and accessible interface across desktop, tablet and mobile devices;
- demonstrate relational database design, CRUD functionality, validation, defensive programming and Django ORM usage.