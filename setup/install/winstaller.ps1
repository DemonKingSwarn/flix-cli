[CmdletBinding()] Param(
    $version = "3.9.9",
    $folder = "C:\Tools"
)
    
$url = "https://www.python.org/ftp/python/$version/python-$version.exe"
$getPip = "get-pip.py"
$bootstrap = "https://bootstrap.pypa.io"
$pipUrl = "$bootstrap/$getPip"
$exec = "$folder\python-$version.exe"
$InstallDir = "$folder\Python$version"

$major = [int]($version.substring(0,1)) # major version
$minor = [int]($version.substring(2,2)) # minor version

if ($major -lt 3 -and $minor -lt 6) {
    Write-Error "Python version $version is not supported for this project"
    exit
}

if($minor -eq 6) {
    $pipUrl = "$bootstrap/pip/3.6/$getPip"
}

if (!(Test-Path -Path $folder)) {
    mkdir -Path "$folder"
}

Write-Output "Downloading Python -version $version"
Write-Output "Running [$exec]..."
(New-Object Net.WebClient).DownloadFile($url, $exec)
& $exec /quiet InstallAllUsers=1 Include_test=0 TargetDir=$InstallDir
if ($LASTEXITCODE -ne 0) {
    throw "The python installer at '$exec' exited with error code '$LASTEXITCODE'"
}
# Write-Output "Setting environment variables for all users..."
[Environment]::SetEnvironmentVariable("PATH", "${env:path};${InstallDir};${InstallDir}/Scripts", "Machine")


Write-Output "Fetching $getPip..."
Set-Location -Path "$InstallDir"
Invoke-WebRequest -Uri $pipUrl -OutFile "$getPip"
Write-Output "Running [py $getPip]..."
py "$getPip" --no-warn-script-location
