# Hinozall Awoken — canonical public build runner

**CURRENT CANONICAL VERSION: Hinozall Awoken 3.5.1**

This repository is the only GitHub repository that should be used as the CI runner for the current Hinozall Awoken build.

Security rule: **never upload any private signing material here**. No `.jks`, keystore, signing password, Instagram credential, cookie, token or session belongs in this public repository. The workflow compiles an **UNSIGNED** release APK only. Final signing is performed privately outside GitHub using the signing material stored in the canonical Ultra archive.

Canonical source flow:
1. decode the current canonical source;
2. apply/verify the final 3.5.1 corrections;
3. refuse the build if key guardrails are missing;
4. compile an unsigned release APK;
5. export the exact patched source.

Latest verified successful build used commit `4e83ed17af70adb7187a1f521a23c6391e321f32` and workflow run `33250994979`.

Do not use old branches or the private `Domniscian/domniscian-build` repository as a source base for future Hinozall modifications.
