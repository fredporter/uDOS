# Contributing to uDOS

First off, thank you for considering contributing to uDOS. Every contribution helps make this project better.

This document provides guidelines for contributing to the project to ensure a smooth and consistent development workflow.

## Development Workflow: The "Development Round"

To maximize efficiency, development is performed in "Rounds." A single Round should encompass a complete, self-contained feature or bug fix, from initial coding all the way through to pushing the changes to the repository.

1.  **Define the Goal for the Round**: Clearly state the overall objective (e.g., "Implement user aliases, update documentation, and deploy the change").

2.  **Plan the Entire Round**: Before writing code, create a comprehensive checklist (TODO list) that includes *all* steps required to achieve the goal:
    *   File creation and modification.
    *   Code implementation for the feature.
    *   Updates to any relevant documentation (like `README.md`).
    *   Local verification (e.g., running the application).
    *   Staging changes (`git add`).
    *   Committing changes with a conventional message (`git commit`).
    *   Pushing the final commit to the remote repository (`git push`).

3.  **Execute the Round Sequentially**:
    *   Work through the checklist systematically, marking tasks as "in-progress" and then "completed."
    *   The entire plan should be executed in a single, uninterrupted session. The goal is to complete all planned tasks without needing intermediate user confirmation, unless a critical error occurs or a decision is required.

4.  **Verify and Report Completion**:
    *   After the final step (the `git push`), provide a summary of the completed Round.
    *   Crucially, ensure all items on the TODO list are marked as "completed" and the list is cleared before concluding the turn.

By adhering to this "Development Round" model, we bundle related actions together, leading to faster progress and more substantial updates with each interaction.
