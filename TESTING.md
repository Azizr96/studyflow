# Testing

> [!NOTE]
> Return to the [README.md](README.md) file.

StudyFlow has been tested throughout development using manual functional
testing, defensive testing, code validation, responsive testing, and
Django system checks.

Detailed user-story testing is documented separately in
[USER_STORY_TESTING.md](USER_STORY_TESTING.md).

---

## Code Validation

Code validation was carried out on the project's HTML, CSS, and Python
code. Third-party libraries such as Bootstrap were not included in the
validation of developer-authored code.

### HTML

The deployed StudyFlow application was tested using the W3C HTML
Validator.

For authenticated Django pages, the rendered page source was copied from
the deployed application using **View Page Source** and validated using
the validator's direct-input option. This ensured that the compiled HTML
was tested rather than Django template syntax.

During validation, actionable HTML and ARIA issues were corrected.

The registration page initially produced four validation errors caused by
Django form help text being rendered through `{{ form.as_p }}`. The form
was changed to render its fields individually while preserving Django's
form validation and help text.

The dashboard also initially produced five ARIA-related validation
errors. These were corrected by adding the appropriate dialog role to
the mobile offcanvas navigation and removing unnecessary `aria-label`
attributes from generic dashboard card containers.

Following these fixes, the actionable errors were removed.

A recurring generic end-of-document `Parse Error` was still reported by
the validator on the tested pages. The generated page source was
inspected and contained the expected closing Bootstrap script, `body`,
and `html` structure. As no specific malformed element was identified,
no speculative code changes were made solely to suppress this message.

| Page | Evidence | Result |
| --- | --- | --- |
| Registration | ![Registration HTML validation](documentation/validation/html/register-validation.png) | Actionable errors corrected; generic end-of-document parse error remained |
| Dashboard | ![Dashboard HTML validation](documentation/validation/html/dashboard-validation.png) | Actionable ARIA errors corrected; generic parse error remained |
| Users | ![Users HTML validation](documentation/validation/html/users-validation.png) | Generic parse error remained |
| Studies | ![Studies HTML validation](documentation/validation/html/studies-validation.png) | Generic parse error remained |
| Study Detail | ![Study Detail HTML validation](documentation/validation/html/study-detail-validation.png) | Generic parse error remained |
| Participants | ![Participants HTML validation](documentation/validation/html/participants-validation.png) | Generic parse error remained |
| Add Participant | ![Participant Form HTML validation](documentation/validation/html/participant-form-validation.png) | Generic parse error remained |
| Visits | ![Visits HTML validation](documentation/validation/html/visits-validation.png) | Generic parse error remained |
| Add Visit | ![Visit Form HTML validation](documentation/validation/html/visit-form-validation.png) | Generic parse error remained |
| Notifications | ![Notifications HTML validation](documentation/validation/html/notifications-validation.png) | Generic parse error remained |
| 404 | ![404 HTML validation](documentation/validation/html/404-validation.png) | Generic parse error remained |
| Log in | ![Log in HTML validation](documentation/validation/html/login-validation.png) | No errors |



---

### CSS

The developer-authored stylesheet at `static/css/style.css` was tested
using the W3C CSS Validator.

The validation returned **no errors**.

Bootstrap is loaded as a third-party dependency and was therefore not
included as developer-authored CSS validation.

| File | Result | Evidence |
| --- | --- | --- |
| `static/css/style.css` | No errors | ![CSS validation](documentation/validation/css/css-validation.png) |

---

### JavaScript

A small amount of custom JavaScript is used within the StudyFlow
`create_study.html` template to improve date selection when creating
a study.

The script listens for changes to the study start date and:

- sets the minimum permitted end date to the selected start date; and
- clears an existing end date if it becomes earlier than the newly
  selected start date.

The JavaScript was validated using JSHint.

JSHint returned no errors or warnings. The reported cyclomatic
complexity for the function was **3**.

| File | Result | Evidence |
| --- | --- | --- |
| `create_study.html` JavaScript | No errors or warnings | ![Create Study JavaScript validation](documentation/validation/javascript/create-study-validation.png) |

The JavaScript provides client-side usability assistance only.
Study date validation is also handled by the Django `StudyForm` on the
server side, so the application does not rely solely on JavaScript for
date validation.

---

### Python

Python code was checked locally with **Flake8** and representative
developer-authored files were additionally validated using the
**Code Institute CI Python Linter**.

The local Flake8 review identified formatting issues including:

- missing final newlines;
- blank-line spacing;
- whitespace on blank lines;
- unused imports;
- indentation;
- line length; and
- import formatting.

These issues were corrected without intentionally changing application
business logic.

Two imports that appear unused to a static analyser are required for
side effects:

- `accounts.signals` is loaded by `AccountsConfig.ready()` to register
  Django signals.
- `env` is loaded locally by `settings.py` to make local environment
  variables available.

These intentional imports use `# noqa: F401`.

After the cleanup, the project was checked with:

```bash
flake8 . --exclude=.venv,migrations,__pycache__,staticfiles,env.py --max-line-length=79
```

Django's own system check was also run:

```bash
python manage.py check
```

Result:

```text
System check identified no issues (0 silenced).
```

The following main project files have also been checked with the
CI Python Linter and returned no errors:

| Application | File | Result | Evidence |
| --- | --- | --- | --- |
| participants | `models.py` | No errors | ![Participants models validation](documentation/validation/python/participants-models-validation.png) |
| participants | `forms.py` | No errors | ![Participants forms validation](documentation/validation/python/participants-forms-validation.png) |
| participants | `views.py` | No errors | ![Participants views validation](documentation/validation/python/participants-views-validation.png) |
| studies | `models.py` | No errors | ![Studies models validation](documentation/validation/python/studies-models-validation.png) |
| studies | `forms.py` | No errors | ![Studies forms validation](documentation/validation/python/studies-forms-validation.png) |
| studies | `views.py` | No errors | ![Studies views validation](documentation/validation/python/studies-views-validation.png) |
| accounts | `models.py` | No errors | ![Accounts models validation](documentation/validation/python/accounts-models-validation.png) |
| accounts | `forms.py` | No errors | ![Accounts forms validation](documentation/validation/python/accounts-forms-validation.png) |
| accounts | `views.py` | No errors | ![Accounts views validation](documentation/validation/python/accounts-views-validation.png) |
| dashboard | `views.py` | No errors | ![Dashboard views validation](documentation/validation/python/dashboard-views-validation.png) |
| notifications | `models.py` | No errors | ![Notifications models validation](documentation/validation/python/notifications-models-validation.png) |
| notifications | `views.py` | No errors | ![Notifications views validation](documentation/validation/python/notifications-views-validation.png) |
| notifications | `utils.py` | No errors | ![Notifications utils validation](documentation/validation/python/notifications-utils-validation.png) |
| studyflow | `settings.py` | No errors | ![Settings validation](documentation/validation/python/settings-validation.png) |

Python migration files, `__pycache__`, the virtual environment,
generated `staticfiles`, and the ignored local `env.py` secrets file
were not treated as developer-authored files requiring CI Python Linter
evidence.

---

## Lighthouse Audit

Google Chrome Lighthouse was used to audit the deployed StudyFlow
application for performance, accessibility, best practices, and SEO.

Testing was carried out using both desktop and mobile Lighthouse
configurations. The public Login page and authenticated Dashboard were
selected as representative pages.

### Lighthouse Results

| Page | Device | Performance | Accessibility | Best Practices | SEO | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Login | Desktop | 100 | 100 | 100 | 100 | ![Login desktop Lighthouse](documentation/lighthouse/login-desktop-lighthouse.png) |
| Login | Mobile | 98 | 100 | 100 | 100 | ![Login mobile Lighthouse](documentation/lighthouse/login-mobile-lighthouse.png) |
| Dashboard | Desktop | 99 | 100 | 100 | 100 | ![Dashboard desktop Lighthouse](documentation/lighthouse/dashboard-desktop-lighthouse.png) |
| Dashboard | Mobile | 97 | 100 | 100 | 100 | ![Dashboard mobile Lighthouse](documentation/lighthouse/dashboard-mobile-lighthouse.png) |

### SEO Improvement

During the initial desktop Lighthouse audit of the Login page, the SEO
score was **90**. Lighthouse identified that the document did not have
a meta description.

A descriptive meta tag was added to the shared `base.html` template:

```html
<meta
    name="description"
    content="StudyFlow is a clinical trial site management system for managing studies, participants, visits, documents, and site activities."
>
```

After the change, `python manage.py check` reported **0 issues**. The
change was deployed and Lighthouse was run again against the deployed
application.

The Login page SEO score increased from **90 to 100**.

The final audits achieved **100 for Accessibility, Best Practices, and
SEO across all four tests**, with Performance scores ranging from
**97 to 100**.

## Browser Compatibility

StudyFlow was manually tested across multiple desktop browsers to
confirm that the deployed application renders consistently and that
core functionality remains operational.

Testing included authentication, navigation, dashboard content,
studies, participants, visits, notifications, forms, tables, buttons,
cards, and responsive navigation.

| Browser | Result | Evidence |
| --- | --- | --- |
| Google Chrome | PASS | ![StudyFlow tested in Google Chrome](documentation/browsers/chrome/chrome-compatibility.png) |
| Microsoft Edge | PASS | ![StudyFlow tested in Microsoft Edge](documentation/browsers/edge/edge-compatibility.png) |
| Mozilla Firefox | PASS | ![StudyFlow tested in Mozilla Firefox](documentation/browsers/firefox/firefox-compatibility.png) |

No browser-specific functional or visual issues were identified during
the manual compatibility testing.