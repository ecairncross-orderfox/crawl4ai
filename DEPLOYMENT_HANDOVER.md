# Crawl4AI URL Discovery Deployment – Handover

## Implemented
- URL discovery helper `map_site`; new API endpoint `POST /map`.
- Verified sitemap-only run for `dmgmori.com` → `dmgmori_urls.json`.
- Added `scripts/aca_deploy.ps1` and updated `DEPLOYMENT_README.md` with `/map`, Docker quick start, ACA usage.

## Intended process (required flow)
1) Local Docker build from repo
2) Push image to Azure Container Registry (ACR)
3) Deploy image from ACR to Azure Container Apps (ACA)

## What ran
- Built and pushed ACR image (OK):
  - `gienijobsacr.azurecr.io/crawl4ai-api:map-202509152354`
- Updated existing ACA (issue persists):
  - Repeated `az containerapp update --image …` attempts; app still reports `unclecode/crawl4ai:latest` and `provisioningState=Failed`.
  - App `registries` shows `null` → registry not bound effectively.
- New ACA from ACR (unclear):
  - `az containerapp create` issued with ACR creds; FQDN not surfaced in captured output → likely create didn’t complete/return as expected in session.

## Likely cause
- ACA not correctly bound to ACR → image pull for new revision fails; template remains on old image.
- Wrong/missing `--container-name` on update can no-op changes (confirm first).
- Failed revision not inspected (need logs/revision details).

## Corrected Azure CLI (per docs)
- Get container name used by the template:
```powershell
az containerapp show -g odx-grp-crawl4ai-prod -n crawl4ai-prod --query "properties.template.containers[].name" -o tsv
```
- Bind ACR to the app (ensures pulls work):
```powershell
$cred = az acr credential show -n gienijobsacr | ConvertFrom-Json
az containerapp registry set `
  -g odx-grp-crawl4ai-prod -n crawl4ai-prod `
  --server gienijobsacr.azurecr.io `
  --username $cred.username `
  --password $cred.passwords[0].value
```
- Update to the tagged image (force new revision):
```powershell
$containerName = "<value from previous command>"
$tag = "gienijobsacr.azurecr.io/crawl4ai-api:map-202509152354"
az containerapp update `
  -g odx-grp-crawl4ai-prod -n crawl4ai-prod `
  --image $tag `
  --container-name $containerName `
  --revision-suffix map-202509152354
```
- If `registries` still null, add creds inline on update:
```powershell
az containerapp update `
  -g odx-grp-crawl4ai-prod -n crawl4ai-prod `
  --image $tag `
  --container-name $containerName `
  --revision-suffix map-202509152354 `
  --registry-server gienijobsacr.azurecr.io `
  --registry-username $cred.username `
  --registry-password $cred.passwords[0].value
```
- Verify image and revisions:
```powershell
az containerapp show -g odx-grp-crawl4ai-prod -n crawl4ai-prod --query "properties.template.containers[0].image" -o tsv
az containerapp revision list -g odx-grp-crawl4ai-prod -n crawl4ai-prod -o table
```
- If revision still fails, inspect why:
```powershell
$rev = az containerapp show -g odx-grp-crawl4ai-prod -n crawl4ai-prod --query "properties.latestRevisionName" -o tsv
az containerapp revision show -g odx-grp-crawl4ai-prod -n crawl4ai-prod --revision $rev -o jsonc
az containerapp logs show -g odx-grp-crawl4ai-prod -n crawl4ai-prod --format text
```
- Test endpoints:
```bash
BASE="https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io"
curl -s $BASE/health
curl -s -X POST $BASE/map -H "Content-Type: application/json" \
  -d '{"root":"dmgmori.com","limit":1000,"source":"sitemap+cc"}'
```

## Fallback: create fresh ACA and cut over
```powershell
$envId = az containerapp show -g odx-grp-crawl4ai-prod -n crawl4ai-prod --query properties.managedEnvironmentId -o tsv
$name  = "crawl4ai-map-" + (Get-Date -Format yyyyMMddHHmmss)
$tag   = "gienijobsacr.azurecr.io/crawl4ai-api:map-202509152354"
$cred  = az acr credential show -n gienijobsacr | ConvertFrom-Json

az containerapp create `
  -g odx-grp-crawl4ai-prod -n $name `
  --environment $envId `
  --image $tag `
  --ingress external --target-port 11235 `
  --registry-server gienijobsacr.azurecr.io `
  --registry-username $cred.username `
  --registry-password $cred.passwords[0].value

az containerapp show -g odx-grp-crawl4ai-prod -n $name --query properties.configuration.ingress.fqdn -o tsv
```

## Next actions
- Bind ACR and update `crawl4ai-prod` with the correct container name + ACR creds inline.
- If revision fails, inspect revision and logs; fix image pull/auth; retry.
- If blocked, create fresh app from the tag, verify `/health` and `/map`, then switch traffic/DNS to it.



