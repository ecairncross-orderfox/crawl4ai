param(
    [Parameter(Mandatory=$true)] [string]$SubscriptionId,
    [Parameter(Mandatory=$true)] [string]$ResourceGroup,
    [Parameter(Mandatory=$true)] [string]$ContainerAppName,
    [Parameter(Mandatory=$true)] [string]$AcrName,
    [string]$ImageTag = "map-" + (Get-Date -Format yyyyMMddHHmm),
    [string]$LlMProvider = "openai/gpt-4o-mini",
    [string]$OpenAiApiKey = $env:OPENAI_API_KEY
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Setting subscription..." -ForegroundColor Cyan
az account set --subscription $SubscriptionId | Out-Null

$registry = "$AcrName.azurecr.io"
$image = "$registry/crawl4ai-api:$ImageTag"

Write-Host "Logging into ACR $AcrName..." -ForegroundColor Cyan
az acr login --name $AcrName | Out-Null

Write-Host "Building image $image (USE_LOCAL=true)..." -ForegroundColor Cyan
docker build -t $image --build-arg USE_LOCAL=true .

Write-Host "Pushing $image..." -ForegroundColor Cyan
docker push $image

Write-Host "Ensuring ingress to port 11235..." -ForegroundColor Cyan
az containerapp ingress set `
  --resource-group $ResourceGroup `
  --name $ContainerAppName `
  --external true `
  --target-port 11235 | Out-Null

Write-Host "Updating container app image and env vars..." -ForegroundColor Cyan
if ([string]::IsNullOrEmpty($OpenAiApiKey)) {
  az containerapp update `
    --resource-group $ResourceGroup `
    --name $ContainerAppName `
    --image $image `
    --set-env-vars LLM_PROVIDER=$LlMProvider | Out-Null
} else {
  az containerapp update `
    --resource-group $ResourceGroup `
    --name $ContainerAppName `
    --image $image `
    --set-env-vars LLM_PROVIDER=$LlMProvider OPENAI_API_KEY=$OpenAiApiKey | Out-Null
}

Write-Host "Done. Current revision:" -ForegroundColor Green
az containerapp show --resource-group $ResourceGroup --name $ContainerAppName --query properties.latestRevisionName -o tsv

Write-Host "Test URLs:" -ForegroundColor Yellow
Write-Host "  Health:   GET  /health" -ForegroundColor Yellow
Write-Host "  Map:      POST /map {root, limit, source}" -ForegroundColor Yellow





