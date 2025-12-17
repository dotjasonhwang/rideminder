---
description: Creates docs/JOURNAL.md with project documentation by analyzing the codebase
---

You are a project documentation assistant. Create a `docs/JOURNAL.md` file with YAML frontmatter by analyzing the current codebase.

## Instructions

1. **Explore the codebase** - Read key files to understand:
   - README.md (if exists)
   - Main source files
   - Package/dependency files (requirements.txt, package.json, etc.)
   - Configuration files (.github/workflows, etc.)
   - Any existing documentation

2. **Extract information**:
   - Project title and summary
   - Tech stack (languages, frameworks, APIs, libraries)
   - Repository URL (from git remote)
   - Architecture and how it works
   - Key implementation details

3. **Create the JOURNAL.md** using this template:

```markdown
---
title: "[Project Name]"
summary: "[One-line description]"
tech_stack:
  - [Technology 1]
  - [Technology 2]
  - [API/Service 1]
repo_url: "[GitHub URL]"
date: "[Today's date YYYY-MM-DD]"
status: "complete"
---

# [Project Name]

## Problem Statement
[What problem does this solve? Infer from README or code purpose]

## Tech Stack
- **Language/Framework**: [List]
- **Infrastructure**: [Deployment/CI/CD]
- **APIs/Services**: [External services used]
- **Key Libraries**: [Important dependencies]

## Architecture

[Use nested bullet structure. DO NOT use bold (**) formatting. Keep concise. Example format:]
- Component A: Description
  - Sub-component: Details
    - Additional details
  - Another aspect: More info

## Challenges
[Leave blank for user to fill]

## Key Decisions
[Identify key architectural decisions from code, like choice of frameworks, deployment platform, etc.]

## What I Learned
[Leave blank for user to fill]

## Future Improvements
[Look for TODO comments, or leave blank]

## Misc Notes
[Any interesting observations from the code]
```

4. **Be thorough** - Read multiple files to get a complete picture
5. **Be specific** - Use actual technology names, versions if available
6. **Infer intelligently** - Make reasonable assumptions about problem statement and architecture
7. **Leave reflective sections blank** - User will fill in Challenges and What I Learned
8. **Formatting** - Use plain markdown bullets, DO NOT use bold (**) formatting in bullet lists

Create the file now.
