$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($Arguments -join ' ')"
    }
}

$repositoryRoot = (& git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Run this script from inside the mlops-course Git repository."
}
Set-Location $repositoryRoot

if (-not (& git remote get-url upstream 2>$null)) {
    throw "The 'upstream' remote is missing. Add it with: git remote add upstream https://github.com/VIHIBXAV054-00/mlops-course.git"
}

$hasLocalChanges = [bool](& git status --porcelain)
$stashCreated = $false

try {
    if ($hasLocalChanges) {
        Write-Host "Parking local changes..."
        Invoke-Git @("stash", "push", "--include-untracked", "-m", "before upstream update")
        $stashCreated = $true
    }

    Write-Host "Updating from upstream/main..."
    Invoke-Git @("pull", "--no-rebase", "upstream", "main")

    if ($stashCreated) {
        Write-Host "Restoring local changes..."
        & git stash pop
        if ($LASTEXITCODE -ne 0) {
            throw "Your changes were restored with conflicts. Resolve them, then commit the result."
        }
    }

    Write-Host "Update completed successfully." -ForegroundColor Green
}
catch {
    Write-Error $_
    if ($stashCreated) {
        Write-Host "Your local changes remain safely stored in git stash. Run 'git stash list' to inspect them." -ForegroundColor Yellow
    }
    exit 1
}