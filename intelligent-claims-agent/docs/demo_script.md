# Demo walkthrough
1. Start Docker services and initialize database.
2. Submit a synthetic claim without documents to demonstrate `awaiting_documents`.
3. Submit a second synthetic claim with claim-form, invoice, and photo text files.
4. Open Claims Queue and Case Workspace to inspect status and summary.
5. Use Approval Center to record a human decision with approver name and rationale.
6. Open Audit History and filter by the case ID.
7. Run `python -m evaluation.run_evaluation` and show the report/release gate.
8. Discuss limitations: OCR not enabled, auth not enforced, graph resume not wired, synthetic policy only.
