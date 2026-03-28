# TPT Release Checklist

## Product Delivery Model

- Sell the resource on Teachers Pay Teachers.
- Deliver a small TPT download that points to the desktop installers.
- Host the actual installers outside TPT on stable file hosting.

## Files To Prepare

- `Start Here.pdf`
- quick install guide
- Windows installer link
- Mac installer link
- system requirements
- support email

## Installer Targets

- Windows: signed `.msi` or signed `setup.exe`
- macOS: signed and notarized `.dmg`

## Hosting

Use stable direct-download hosting such as:

- S3 / CloudFront
- Dropbox
- Google Drive direct download links

## TPT Listing Guardrails

- Do not require buyers to create another account just to use the app.
- Do not route buyers to another checkout flow for the real product.
- Do not upload a raw `.exe` without an installer.
- Do not rely on unsigned desktop builds for public release.

## Final Pre-Publish Check

- Verify both installers download in one click.
- Test the Windows installer on a clean Windows machine.
- Test the Mac installer on a clean Mac.
- Confirm the support email is visible in the guide.
- Confirm the Start Here guide explains how to choose the right installer.
