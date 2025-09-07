# Google Cloud CLI Installation Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "🚀 Installing Google Cloud CLI for Windows..." -ForegroundColor Green

# Check if winget is available
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "📦 Installing Google Cloud SDK using winget..." -ForegroundColor Yellow
    winget install Google.CloudSDK
} else {
    Write-Host "📥 Downloading Google Cloud SDK installer..." -ForegroundColor Yellow
    
    # Download the installer
    $installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
    $installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"
    
    try {
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        Write-Host "✅ Download completed" -ForegroundColor Green
        
        # Run the installer
        Write-Host "🔧 Running installer..." -ForegroundColor Yellow
        Start-Process -FilePath $installerPath -Wait
        
        # Clean up
        Remove-Item $installerPath -Force
        Write-Host "✅ Installation completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Download failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please download manually from: https://cloud.google.com/sdk/docs/install-sdk#windows" -ForegroundColor Yellow
        exit 1
    }
}

# Refresh environment variables
Write-Host "🔄 Refreshing environment variables..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify installation
Write-Host "🧪 Verifying installation..." -ForegroundColor Yellow
try {
    gcloud --version
    Write-Host "✅ Google Cloud CLI installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Installation may need a restart to take effect" -ForegroundColor Yellow
    Write-Host "Please restart your terminal and run: gcloud --version" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Restart your terminal/PowerShell" -ForegroundColor White
Write-Host "2. Run: gcloud auth login" -ForegroundColor White
Write-Host "3. Run: gcloud config set project tetris-effect-469618-t1" -ForegroundColor White
Write-Host "4. Run: ./deploy.sh tetris-effect-469618-t1" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Ready to deploy FLUX-LanternHive to Google Cloud!" -ForegroundColor Green


