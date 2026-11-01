# Copilot Instructions

This repository must maintain a living design record and an implementation record under the `specs/` directory.

## Required documents

- `specs/design.md`: capture the design decisions for the product or feature. Include architecture choices, trade-offs, constraints, assumptions, risks, and any decisions that resolve ambiguity in the design.
- `specs/implementation.md`: describe the actual implementation details. Explain how the code and system are built, which files/modules are involved, key flows, edge cases, and where the design was ambiguous or required interpretation during implementation.

## Expectations

- Create both files as soon as the work begins and keep them updated as the project evolves.
- Keep the design doc focused on decisions, rationale, and intent.
- Keep the implementation doc focused on execution details and real-world implementation choices.
- When a requirement or design is ambiguous, document the ambiguity in the design doc and the chosen resolution in the implementation doc.
- If the implementation diverges from the original design, explain the divergence and why it was necessary.

## Workflow

1. Draft and maintain the design decisions in `specs/design.md`.
2. Record implementation specifics in `specs/implementation.md`.
3. Update both docs whenever scope, architecture, or implementation changes.
4. Treat both docs as part of the source of truth alongside code.
