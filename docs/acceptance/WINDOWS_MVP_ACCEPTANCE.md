# AURORA — first usable Windows acceptance

This is a manual acceptance checklist for a **separate clean Windows x64 PC**.
It is not a claim that the checks have passed. Automated offline browser tests
and the packaged-executable CI smoke test do not substitute for this journey.
Use a disposable test business idea and avoid entering private client data.

## Prepare the candidate

1. Record the exact `master` commit SHA to test. In the repository's GitHub
   **Actions → Portable Windows** page, select a successful run for that SHA
   and download its `AURORA-Windows-x64` artifact. The artifact contains
   `AURORA-Windows-x64.zip`; it is not a GitHub Release or signed installer.
2. On the target Windows x64 PC, confirm Python, uv, Node and pnpm are **not**
   installed for this test. Record the Windows version and whether the PC is
   new or merely an isolated profile. A profile on a developer PC does not
   qualify as a clean-PC result.
3. Extract the ZIP with Windows Explorer into a new directory. Do not run the
   executable inside the compressed archive. Run `AURORA\AURORA.exe`; verify
   that the local browser UI opens and that the console remains available to
   stop the foreground app with Ctrl+C. If Windows security blocks an unsigned
   executable, record **BLOCKED**; do not disable protection or describe the
   build as signed.
4. Verify the browser address is `http://127.0.0.1:<port>/`, not a public
   interface. Do not share the local URL or expose its port to the network.

## Mandatory user journey

Mark each item PASS, FAIL, BLOCKED or NOT RUN. Record a concise non-secret
observation for any result other than PASS.

| ID | Action and observable result | Result |
| --- | --- | --- |
| M01 | On first launch, select Русский or English and finish the guide. Open Settings, switch to the other language, save, close and reopen the app; the choice and completed guide persist. Reopen the guide from the toolbar. | NOT RUN |
| M02 | Enter a test OpenAI API key in Settings directly in the app. The UI reports a connected key; it does not show the key again. Do not paste or photograph the key in this record. | NOT RUN |
| M03 | On Projects, enter a project name and one business prompt. Select **Generate from prompt** and explicitly confirm the potentially charged text request. Verify a brand, page/section content and SEO draft appears for review, and is labelled unsaved. | NOT RUN |
| M04 | Review the draft and explicitly accept it. The new project opens in the editor. A failed or rejected draft must not be reported as saved. | NOT RUN |
| M05 | Use the guided image completion in the editor for at least one empty logo/section target. Review its prompt, supply section-image alt text when required, separately confirm the potentially charged image request, review the returned image and attach it to the selected target. This is **not** unattended one-prompt image generation. | NOT RUN |
| M06 | Manually change a brand field, page or section text and one page SEO field. Collapse and reopen the left and right panels independently. Save and verify the editor reports the saved state. | NOT RUN |
| M07 | Open desktop and mobile-width preview, then open the saved preview in a browser tab. Verify the accepted edits and attached image appear; broken assets or stale text are a FAIL. | NOT RUN |
| M08 | Stop AURORA with Ctrl+C, relaunch the same extracted executable, reopen the project from Projects and verify the edits and image persisted. | NOT RUN |
| M09 | In Export & deploy, export a site folder and download the ZIP. Open the exported `index.html` and any additional generated page, if present. Verify the static site renders, includes its referenced assets, and contains neither project-state JSON nor credential files. | NOT RUN |
| M10 | Inspect the app's displayed projects directory: it should be under `%USERPROFILE%\Documents\AURORA\Projects\`. Confirm that project files are separate from `%LOCALAPPDATA%\AURORA\settings.json`. Inspect file **names and structure only**; do not copy secret material into evidence. | NOT RUN |

Text and image generation in M03/M05 contact OpenAI and may cost money. The
operator must choose to confirm those calls at action time. Without an
available account/key, mark them BLOCKED and do not claim full acceptance.
An interrupted request with an uncertain outcome must be checked before a
retry; do not click retry automatically. Project data must not be deleted to
rerun the checklist.

## Optional publication journey

Netlify deployment is optional for the ADR-002 first usable path. It publishes
the static site to a public URL and requires separate action-time consent.

| ID | Action and observable result | Result |
| --- | --- | --- |
| O01 | Enter a Netlify token directly in Settings. Use **Deploy to Netlify**, read the publication confirmation and approve it only if publication is intended. Verify a public URL is returned and the deployed site renders. | NOT RUN |
| O02 | If the app says the deployment outcome is uncertain, inspect Netlify for an existing deployment before any retry; do not infer failure or create a duplicate deployment. | NOT RUN |

Do not publish a real business or sensitive content merely to complete this
checklist. Do not paste the Netlify token into an issue, PR or chat.

## Evidence and decision record

Fill a copy of this section outside the repository if it contains machine or
account details. A maintainer may publish only a redacted summary.

```text
Candidate commit SHA:
Portable Windows workflow run URL / artifact name:
Target Windows version and x64 confirmation:
Clean-PC status (not a developer PC):
Tester and date:
Mandatory results M01–M10:
Optional results O01–O02:
Non-secret failure/blocked observations:
Overall: PASS / FAIL / BLOCKED / NOT RUN
```

Overall **PASS** requires M01–M10 to pass on the exact candidate with actual
OpenAI text and image responses. O01–O02 are optional and must be reported
separately. If any mandatory step is failed, blocked or not run, the first
usable Windows journey remains **unverified**. A public release, signed-binary
claim or production deployment requires its own decision and is not authorized
by this checklist.
