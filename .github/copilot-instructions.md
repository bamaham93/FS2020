# GitHub Copilot Instructions for FS2020

## Working Directory
- **IMPORTANT**: The repository must be run from the root folder (`/home/runner/work/FS2020/FS2020`), NOT from the `python_anywhere_website` folder
- When running Django commands, use: `python python_anywhere_website/manage.py <command>`

## Documentation
- Keep all documentation up to date, including the `README.md` file
- Document any new features, changes to existing features, or architectural decisions
- Update relevant docstrings when modifying functions or classes

## Communication
- Ask any clarifying questions that are needed before proceeding with implementation
- Don't make assumptions about requirements - verify with the development team

## Branching and Version Control
- Feature branches are a good thing - create them for new features or significant changes
- Branch naming convention: use descriptive names (e.g., `feature/add-user-auth`, `fix/login-bug`)
- Commits should encompass one thing, feature, or area of the app
- Write clear, descriptive commit messages

## Code Style and Formatting
- **Black** is the linter of choice; comply with Black's formatting whenever possible
- Comply with Python's **PEP8** unless it conflicts with Black
- When in doubt, Black takes precedence over PEP8
- Run Black before committing: `black .` from the root directory

## Dependencies
- Within reason, try to minimize external dependencies
- Check with the dev team if there is any question as to whether a package makes sense for the project
- Always update `requirements.txt` when adding new dependencies
- Prefer using packages already in the project when possible

## Testing
- **Test-Driven Development (TDD)** is a good thing
- At the least, we should try for reasonable test coverage on any new features
- Run tests with: `python python_anywhere_website/manage.py test`
- Write tests for:
  - New features
  - Bug fixes
  - Edge cases
  - Critical business logic

## Definition of "Ready to Merge"

A PR is merge-ready when ALL of the following criteria are met:

1. **Tests pass**: Run `python python_anywhere_website/manage.py test` successfully
2. **Black formatting is clean**: Code passes Black formatting checks
3. **Documentation is updated**: README.md and relevant docs reflect changes
4. **Changes match the scoped requirements**: Implementation aligns with the issue/feature requirements
5. **No secrets are introduced**: No API keys, passwords, or sensitive data in code
6. **PR description includes verification steps**: Clear steps to verify the changes work as intended

### Pre-Merge Checklist
- [ ] All tests pass locally
- [ ] Black formatting applied and passes
- [ ] Documentation updated
- [ ] No secrets or credentials committed
- [ ] PR description includes verification steps
- [ ] Changes are scoped to the requirements
- [ ] Code reviewed and approved

## Project-Specific Notes
- This is a Django 5.0.4 project (originally generated with Django 4.0.4)
- The project includes multiple Django apps: fs2020, core_app, douglas, resume, prayer, media_app, finance
- Main project settings are in `python_anywhere_website/main_app/` directory
- SQLite is used for the database
- The project is deployed to PythonAnywhere
- CI/CD runs on GitHub Actions (see `.github/workflows/django.yml`)
