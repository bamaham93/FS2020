# AI Coding Rules - GA-Local Repository

This document consolidates all AI coding rules and guidelines from the GA-Local repository. You can apply these same rules to other repositories by copying the relevant sections.

---

## Source Documents
- **CONTRIBUTING.md**: General contribution guidelines including AI-specific rules
- **.github/copilot-instructions.md**: Project-specific technical instructions for AI agents

---

## 1. General AI Contribution Rules

### 1.1 Human Review & Approval
- **All AI-generated code must be reviewed and approved by a human maintainer** before being merged
- AI-generated changes must be submitted as pull requests
- Clearly label issues or pull requests with an `[AI-Generated]` tag
- Provide detailed descriptions explaining the intent and logic behind proposed changes

### 1.2 Coding Standards
- AI-generated code must conform to the repository's existing conventions, including:
  - Naming standards
  - Formatting
  - Modularity
- Maintain consistency with the existing codebase

---

## 2. Restricted Actions

### 2.1 Sensitive Files (No Direct AI Modification)
AI **must not make direct changes** to:
- `README.md`
- `LICENSE`
- Deployment scripts
- Core configuration files
- Production database files (e.g., `db.sqlite3`)

### 2.2 Restricted Autonomy
- AI **cannot independently resolve or close issues**
- AI **cannot merge pull requests autonomously**
- AI may propose breaking down large issues into smaller tasks if requested
- AI cannot add, remove, or modify project dependencies without prior approval

---

## 3. Testing & Validation Requirements

### 3.1 Mandatory Testing
- **All AI-generated code must include thorough tests** for new functionality
- Changes must pass all existing automated tests before review
- No AI-generated code should skip or weaken test coverage
- **CRITICAL**: Always run the test suite before completing any issue, feature, or bugfix

### 3.2 Test Execution
Before submitting any PR:
1. Run the repository's test suite
2. Run linters and formatters
3. Verify all tests pass
4. Document any test-related changes

### 3.3 Backward Compatibility
- AI may suggest optimizations but must maintain backward compatibility
- Never remove or modify working code without justification

---

## 4. Data Safety & Database Management

### 4.1 Database Protection
- **Never delete the database**: Under no circumstances should AI agents delete or overwrite production or development database files
- All database-modifying operations must be deliberate, documented, and reversible
- Tests must run against ephemeral test databases only
- Local tests should use framework-managed test databases (e.g., Django's test runner creates and destroys these automatically)

### 4.2 Database Migrations (for Django projects)
- **All database schema changes MUST be made through the migration system**
- Never manually modify database schema using SQL, database tools, or direct access
- Follow the proper workflow:
  1. Modify the model in code
  2. Create migration files
  3. Review migration files
  4. Test migrations locally
  5. Commit migration files to git
  6. Push to repository

**Never:**
- Skip migrations or apply them selectively
- Modify migration files after they've been applied
- Use SQL commands (`ALTER TABLE`, `CREATE TABLE`, etc.) instead of migrations
- Use database GUI tools to modify schema

---

## 5. Feature Development & Branching

### 5.1 Feature Branches
- Use feature branches to prevent accidental deployment of experimental features
- When creating a feature branch, also create a Pull Request to merge back into main
- Do not push experimental changes directly to `main`
- Open PRs early to enable ongoing review

---

## 6. Documentation Requirements

### 6.1 Documentation Updates
- AI-generated changes should update relevant documentation to reflect modifications
- Update usage guides, comments, and related docs
- AI can assist in drafting new sections or improving clarity but requires explicit review

---

## 7. Security & Dependencies

### 7.1 Dependency Management
- AI must not add, remove, or modify project dependencies without prior approval
- All dependency changes must be reviewed for:
  - Licensing compatibility
  - Security vulnerabilities
  - Version compatibility
- Before adding new dependencies, use security advisory tools to check for vulnerabilities

### 7.2 Security Compliance
- AI must avoid introducing code that could compromise application security or user data
- Contributions must adhere to industry best practices for secure software development
- Run security scanning tools (like CodeQL) before finalizing changes

---

## 8. Feedback & Continuous Improvement

### 8.1 Accountability
- Any issues, bugs, or unexpected behavior stemming from AI-generated changes must be:
  - Documented
  - Reported
  - Prevented in future contributions

### 8.2 Iterative Improvement
- These rules should be periodically revisited and refined based on experience
- Gather feedback from maintainers about AI contributions
- Update guidelines as needed

---

## 9. Project-Specific Implementation Notes

When adapting these rules for a specific project, add sections for:

### 9.1 Project Structure
- Project type and framework
- Key files to read before making changes
- Configuration file locations
- Canonical entrypoints

### 9.2 Developer Workflows
- Commands for setting up development environment
- Commands for running tests
- Commands for running linters/formatters
- Commands for building/running the application

### 9.3 Project Conventions
- Template/view patterns
- Code organization patterns
- Naming conventions
- Common pitfalls to avoid

### 9.4 Pre-submission Checklist
Create a checklist that AI should follow before submitting changes, such as:
1. Run linters/formatters
2. Read key configuration files to understand impact
3. Avoid committing credentials or secrets
4. Run tests locally
5. Create minimal, focused changes

---

## 10. How to Apply These Rules to Another Repository

### Step 1: Create Contributing Guidelines
Create or update a `CONTRIBUTING.md` file with:
- Sections 1-8 from this document (adapt as needed)
- Project-specific database/migration rules if applicable
- Security scanning requirements

### Step 2: Create AI Agent Instructions
Create `.github/copilot-instructions.md` (or similar) with:
- Project structure overview
- Key files to read before changes
- Developer workflow commands
- Project-specific conventions
- Common pitfalls
- Pre-submission checklist

### Step 3: Add Security Scanning
- Configure CodeQL or similar security scanning tools
- Add dependency vulnerability checking
- Require security scans to pass before merge

### Step 4: Configure CI/CD
- Ensure automated tests run on all PRs
- Add linter/formatter checks to CI
- Add security scanning to CI pipeline

### Step 5: Document Database Management
If your project uses databases:
- Document the migration workflow
- Specify protected database files
- Add safeguards in CI/automation

---

## Example File Structure

```
your-repo/
├── CONTRIBUTING.md           # General contribution guidelines (Sections 1-8)
├── .github/
│   └── copilot-instructions.md  # AI agent technical instructions (Section 9)
└── .github/workflows/
    └── ci.yml                # Automated testing and validation
```

---

## Key Takeaways

1. **Human oversight is mandatory** - AI assists but doesn't replace human judgment
2. **Testing is non-negotiable** - All changes must include and pass tests
3. **Data safety first** - Never risk production data
4. **Security matters** - Screen dependencies and scan for vulnerabilities
5. **Documentation is essential** - Keep docs in sync with code
6. **Feature branches protect production** - Never commit experiments to main
7. **Minimal, focused changes** - Small PRs are easier to review and safer

---