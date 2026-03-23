function Show-Help {
    Write-Host "Available commands:"
    Write-Host "  ./scripts/dev.ps1 run    - Start the FastAPI application"
    Write-Host "  ./scripts/dev.ps1 test   - Run all backend tests with pytest"
    Write-Host "  ./scripts/dev.ps1 lint   - Check code quality with ruff"
    Write-Host "  ./scripts/dev.ps1 format - Format code with black and ruff"
}

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("run", "test", "lint", "format", "help")]
    $Action
)

switch ($Action) {
    "run" {
        uvicorn app.main:app --reload
    }
    "test" {
        pytest tests/ -v -s -rP
    }
    "lint" {
        ruff check .
    }
    "format" {
        black .
        ruff check . --fix
    }
    "help" {
        Show-Help
    }
}
