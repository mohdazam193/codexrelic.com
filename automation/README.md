# Automation Approach

Scripts that automate the manual steps being done for learning.
Each script mirrors exactly one section of the manual setup guides.

> Run these scripts when you want to repeat a setup quickly, onboard a new environment,
> or recover from scratch. For first-time learning, do the manual steps first.

---

## Scripts

| # | Script | Manual equivalent | Status |
|---|--------|-------------------|--------|
| 01 | `01-auth-setup/generate-keys.sh` | AUTH_SETUP.md Steps 1–3 | ✅ Ready |
| 02 | `02-keyvault/create-and-populate-keyvaults.sh` | Implementation Plan Parts 2–3 | ✅ Ready |

---

## Usage

```bash
# Make all scripts executable (run once)
find automation -name "*.sh" -exec chmod +x {} \;

# Run a specific script
bash automation/01-auth-setup/generate-keys.sh
bash automation/02-keyvault/create-and-populate-keyvaults.sh
```

---

## Adding New Scripts

When a new manual task is completed and should be automated, add a row to the table above
and create the corresponding script in a numbered folder.

Naming convention: `<nn>-<topic>/<verb>-<noun>.sh`
