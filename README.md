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

## UX

### The 5 Planes of UX

The UX design for StudyFlow was planned using the Five Planes of User Experience: Strategy, Scope, Structure, Skeleton and Surface. This approach helped ensure that the application's features were based on genuine user requirements rather than designing individual pages without considering the overall workflow.

### 1. Strategy

#### Purpose

StudyFlow was designed to provide clinical trial site staff with a centralised interface for managing fictional clinical studies, participants, visits, study documents and user assignments.

The system aims to reduce the need to navigate between disconnected information by organising the main site-management activities around individual clinical studies.

The application also places particular importance on access control. Users should only be able to access information and functionality appropriate to their role and assigned studies.

#### Primary User Needs

StudyFlow has two primary groups of authenticated users.

**Elevated users - Administrators, Investigators and Project Leads**

These users need to:

- approve or reject new account registrations;
- manage registered users;
- assign appropriate roles to users;
- assign users to clinical studies;
- create new studies;
- view all studies and associated information;
- monitor activity across the application;
- access an overview of study, participant and visit activity through the dashboard.

**Standard users - Study Coordinators and Trial Assistants**

These users need to:

- access only the studies assigned to them;
- view study information without modifying the core study details;
- upload documents to assigned studies;
- create, view, update and delete fictional participants within assigned studies;
- create, view, update and delete participant visits;
- receive notifications relating to activity within their assigned studies;
- use a dashboard containing information relevant to their assigned studies.

#### Project Goals

The main project goals are to:

- provide a simple and structured clinical trial site management interface;
- demonstrate secure authentication and authorisation;
- implement role-based and study-based access control;
- provide useful CRUD functionality using Django and PostgreSQL;
- provide clear feedback following important user actions;
- maintain relationships between users, studies, participants, visits and documents;
- provide relevant notifications about study activity;
- create an interface that remains usable across desktop, tablet and mobile devices;
- follow accessibility and defensive programming principles.

### 2. Scope

The scope of StudyFlow was deliberately controlled so that the project could deliver a complete and functional MVP within the available development period.

#### Core Features

The MVP includes:

- user registration;
- administrator approval of new accounts;
- login and logout;
- role-based permissions;
- user management;
- study assignment;
- study creation;
- role-aware study lists;
- study detail pages;
- study document uploads;
- participant CRUD functionality;
- visit CRUD functionality;
- role-aware dashboards;
- database-backed notifications;
- responsive navigation and page layouts;
- server-side form validation;
- destructive-action confirmation.

#### Content Requirements

StudyFlow stores and displays information relating to:

- users and their assigned roles;
- study assignments;
- study protocol information;
- fictional participant information;
- scheduled and completed visits;
- uploaded study documents;
- user notifications.

The participant data used within StudyFlow is entirely fictional and exists only to demonstrate application functionality.

#### Features Outside the MVP

To prevent scope creep, several features were intentionally excluded from the initial version of StudyFlow.

These include:


- storage of real patient or clinical trial data.
- real-time WebSocket notifications.
- advanced analytics.
- regulatory-grade audit logging.

Some additional features were retained as Should Have or Could Have user stories and may be implemented if development time permits.

### 3. Structure

#### Information Architecture

StudyFlow follows a study-centred information structure.

The main relationship is:

**Study → Participants → Visits**

A study can contain multiple fictional participants, and each participant can have multiple visits.

Studies can also contain uploaded study documents and can have multiple users assigned to them.

Users receive notifications relevant to activity within studies to which they have been assigned.

#### Navigation

Authenticated elevated users can access:

- Dashboard
- Studies
- Participants
- Visits
- Notifications
- Users
- Logout

Authenticated standard users can access:

- Dashboard
- Studies
- Participants
- Visits
- Notifications
- Logout

The **Users** area is deliberately excluded from the standard-user navigation because user administration is restricted to authorised elevated roles.

On desktop devices, navigation is provided through a persistent left sidebar.

On tablet and mobile devices, the sidebar is replaced with a hamburger menu which opens the navigation when required. A persistent mobile bottom navigation was intentionally avoided to maintain a clean interface and prevent unnecessary duplication.

#### User Flow

A typical elevated-user flow is:

1. Log in to StudyFlow.
2. Review the global dashboard.
3. Review pending registrations.
4. Approve a user and assign an appropriate role.
5. Create or view a study.
6. Assign users to the study.
7. Monitor study, participant, visit and document activity.

A typical standard-user flow is:

1. Register for a StudyFlow account.
2. Wait for account approval and role assignment.
3. Log in after approval.
4. View the assigned-study dashboard.
5. Open an assigned study.
6. Manage fictional participants within that study.
7. Schedule and update participant visits.
8. Upload relevant study documents.
9. Review notifications relating to assigned-study activity.

### 4. Skeleton

The StudyFlow interface was designed around a consistent application shell so that users do not need to relearn the interface when moving between different areas.

The main page structures include:

- authentication forms for registration and login.
- dashboard statistic cards and activity tables.
- study list and study detail pages.
- participant and visit tables.
- create and update forms.
- confirmation pages for destructive actions.
- user-management screens.
- notification lists.
- responsive desktop, tablet and mobile navigation.

Tables are used where users need to compare structured information, while cards and forms are used where information needs greater visual separation.

Initial wireframes were produced for desktop, tablet and mobile layouts before the main interface was implemented. These are documented in the [Wireframes](#wireframes) section.

### 5. Surface

**Visual Design Elements**

- [**Colour Scheme**](#colour-scheme) (see below)
- [**Typography**](#typography) (see below)

The visual design of StudyFlow was created to provide a clean, professional and structured interface appropriate for a clinical trial site management application. The design deliberately avoids excessive decoration so that studies, participants, visits, documents and notifications remain the main focus of each page.

### Colour Scheme

StudyFlow uses a restrained blue, white and neutral-grey colour palette. Dark navy is used for the primary navigation to provide a strong visual structure, while lighter backgrounds are used throughout the main content area to keep data-heavy pages clear and readable.

Blue is used for primary actions and interactive emphasis, while red is reserved for destructive actions and validation feedback. Status information also includes visible text so that meaning is not communicated through colour alone.

The main colours used throughout StudyFlow are:

- `#17324D` — primary dark navy used for the desktop sidebar and mobile navigation header. This provides strong separation between the main navigation and application content.
- `#F5F7FA` — light grey page background used behind the main application content to reduce the visual harshness of a completely white interface.
- `#FFFFFF` — white used for cards, forms, tables and other primary content surfaces.
- `#0D6EFD` — Bootstrap primary blue used for primary actions, links, focus indicators and interface emphasis.
- `#198754` — Bootstrap success green used for positive and completed states where appropriate.
- `#DC3545` — Bootstrap danger red used for destructive actions such as deletion.
- `#B02A37` — dark red used for form validation error messages to clearly distinguish invalid input.
- `#6C757D` — muted grey used for secondary information and form help text.
- `#E1E6EB` — light border colour used around cards, tables and notification containers.
- `#EEF2F6` — light interaction background used when navigation items are hovered or focused.

The palette was selected to maintain a professional clinical appearance while providing clear visual distinction between navigation, content, actions, status information and warnings.

Colour is not relied upon as the only method of communicating important information. For example, notification states and application statuses also contain descriptive text.


![StudyFlow colour palette](documentation/color-pallete.png)

### Typography

StudyFlow uses the default Bootstrap system font stack rather than importing external Google Fonts.

Using a system font stack allows the application to use fonts already available on the user's operating system. This provides a familiar appearance, reduces the need for additional font downloads and helps maintain consistent readability across different devices and browsers.

Typography follows a clear hierarchy:

- headings are used to identify pages and major content sections;
- bold and semi-bold text is used for navigation, form labels and important information;
- standard body text is used for descriptions and application content;
- smaller muted text is used for secondary information and form guidance;
- larger bold values are used on dashboard statistic cards to make important figures easy to identify.

Bootstrap's responsive typography and spacing are combined with custom CSS to maintain consistency across desktop, tablet and mobile layouts.

No external icon library is currently required for the core StudyFlow interface. Bootstrap's built-in components and standard text labels are used for navigation and actions.

## Wireframes

Wireframes were created during the planning stage of StudyFlow to establish the application's information hierarchy, navigation and responsive layout before detailed visual styling was applied.

The wireframes were intentionally kept low-fidelity. They use simple boxes, placeholder content and minimal visual styling because their purpose was to plan the position and relationship of interface elements rather than represent the final appearance of the application.

Separate layouts were considered for elevated users and standard users because the information and functionality available to each role differs.

Elevated users such as Administrators, Investigators and Project Leads require access to user management and application-wide information, while Study Coordinators and Trial Assistants require an interface focused on their assigned studies.

Responsive layouts were also considered from the beginning. Desktop designs use a persistent sidebar, while tablet and mobile designs replace this with a hamburger navigation menu to preserve screen space.

### Dashboard Wireframes

The dashboard wireframes demonstrate how the interface adapts according to both user role and screen size.

| Desktop | Tablet | Mobile |
| --- | --- | --- |
| Elevated user dashboard | Elevated user dashboard | Elevated user dashboard |
| Standard user dashboard | Standard user dashboard | Standard user dashboard |

![StudyFlow dashboard wireframes](documentation/wireframes/users-dashboard.png)

### Application Wireframes

Additional wireframes were created for the main workflows within StudyFlow, including:

- login and registration.
- user management.
- studies list.
- study details.
- participant management.
- visit forms.
- study documents.
- notifications.
- confirmation screens.

These wireframes were used as a structural guide during development. Some elements evolved during implementation as usability, permissions and technical requirements became clearer.

![StudyFlow application wireframes](documentation/wireframes/All-page-wireframes.png)

### Changes From the Initial Wireframes

The wireframes were treated as a guide rather than a fixed specification. During development, several interface decisions were refined after testing the application in the browser.

Examples include:

- responsive navigation was implemented using a persistent sidebar on desktop and a hamburger/offcanvas menu on tablet and mobile.
- user study assignments were moved into a dedicated user detail workflow rather than overloading the main users list.
- destructive actions were given dedicated confirmation pages to reduce accidental deletion.
- study core information remained read-only after creation, while authorised users can manage associated participants, visits and documents.
- dashboard information became role-aware so standard users only see information associated with their assigned studies.
- notification previews were incorporated into the dashboard while the full notification history remains available from the Notifications page.

These changes demonstrate the iterative development process between the original UX planning and the final implementation.

## User Stories

User stories were used throughout the development of StudyFlow to define functionality from the perspective of the application's users.

The stories were managed using GitHub Issues and the StudyFlow GitHub Project board. Each story was prioritised using the MoSCoW method and moved through the development workflow:

**Todo → In Progress → Testing → Done → Future Additions**

Detailed acceptance criteria are maintained within the corresponding GitHub Issues, while the tables below provide an overview of the requirements used to guide development.

### Must Have User Stories

The following user stories formed the core MVP requirements for StudyFlow.

| ID | User Story |
| --- | --- |
| US01 | As a new user, I want to register for an account so that I can request access to StudyFlow. |
| US02 | As an authorised elevated user, I want to approve or reject registrations so that only authorised users can access the system. |
| US03 | As an approved user, I want to log in securely so that I can access functionality appropriate to my role. |
| US04 | As an authenticated user, I want to log out securely so that my account is protected when I finish using the application. |
| US05 | As a user, I want the interface to reflect my authentication state so that I can clearly understand whether I am logged in and which functionality is available to me. |
| US06 | As an authorised elevated user, I want to search for and view registered users so that I can manage application access efficiently. |
| US07 | As an authorised elevated user, I want to assign users to studies so that staff can access the studies they are responsible for. |
| US08 | As an authorised elevated user, I want to delete a user when necessary so that obsolete accounts can be removed securely. |
| US09 | As an authorised elevated user, I want to create a study so that new clinical trial studies can be managed within StudyFlow. |
| US10 | As an elevated user, I want to view all studies so that I can oversee study activity across the application. |
| US11 | As a standard user, I want to view only studies assigned to me so that I only access information relevant to my responsibilities. |
| US12 | As an authorised study user, I want to upload study documents so that relevant documentation can be stored against the appropriate study. |
| US13 | As an authorised study user, I want to add a fictional participant to a study so that participant activity can be managed. |
| US14 | As an authorised user, I want to view fictional participants associated with accessible studies so that I can review participant information. |
| US15 | As an authorised study user, I want to update a fictional participant so that their study information can be kept current. |
| US16 | As an authorised study user, I want to delete a fictional participant so that incorrectly created or unnecessary records can be removed. |
| US17 | As an authorised study user, I want to add a visit for a participant so that study visits can be scheduled and tracked. |
| US18 | As an authorised user, I want to view visits associated with accessible studies so that I can monitor visit activity. |
| US19 | As an authorised study user, I want to update a visit so that its status, dates and notes can be maintained. |
| US20 | As an authorised study user, I want to delete a visit so that incorrect or unnecessary visit records can be removed. |
| US21 | As an elevated user, I want a global dashboard so that I can see an overview of activity across the application. |
| US22 | As a standard user, I want a personalised dashboard so that I only see information associated with my assigned studies. |
| US23 | As a user, I want to receive relevant notifications so that I am aware of important activity relating to my studies. |
| US24 | As a user, I want to view and mark notifications as read so that I can manage information that requires my attention. |
| US25 | As a user, I want the application to work across desktop, tablet and mobile devices so that I can use StudyFlow on different screen sizes. |
| US26 | As a user, I want an accessible interface so that StudyFlow is understandable and operable for users with different accessibility requirements. |

### Should Have User Stories

These stories provide useful improvements to the core application but are not required for the initial MVP to function.

| ID | User Story |
| --- | --- |
| US27 | As a user, I want to filter studies by status so that I can find relevant studies more efficiently. |
| US28 | As a user, I want to search participants so that I can locate a fictional participant without manually reviewing the entire list. |
| US29 | As a user, I want to filter visits so that I can more easily review relevant visit activity. |

### Could Have User Stories

These stories were identified as potential enhancements if sufficient development time remained after completion and testing of the core application.

| ID | User Story |
| --- | --- |
| US30 | As an authorised user, I want enhanced dashboard charts so that application activity can be visualised more easily. |
| US31 | As an elevated user, I want an activity audit log so that important actions within StudyFlow can be reviewed. |
| US32 | As a study user, I want a visit progress indicator so that I can quickly understand a participant's progress through their study visits. |

### MoSCoW Prioritisation

The MoSCoW method was used to control the project scope within the available development period.

**Must Have** stories represent the core StudyFlow MVP. These include authentication, permissions, studies, participants, visits, dashboards, notifications, responsiveness and accessibility.

**Should Have** stories improve usability but do not prevent the core application from operating if they are not completed.

**Could Have** stories represent enhancements that were deliberately kept outside the core MVP until the essential functionality had been implemented and tested.

This prioritisation helped prevent scope creep and ensured that development remained focused on delivering a secure and functional application before optional enhancements were considered.