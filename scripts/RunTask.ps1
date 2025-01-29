param (
    [string]$ExecutableCommand  # Command to run, including the full path to the executable and any arguments
)

function Get-MostRecentSessionID {
    $username = [Environment]::UserName
    $queryOutput = query session $username
    $activeSessionLines = @($queryOutput | Where-Object { $_ -match "\b$username\b" -and $_ -match "Active" })

    Write-Host "Number of active sessions: $($activeSessionLines.Length)"

    if ($activeSessionLines) {
        $activeSessionLine = $activeSessionLines[-1]
        $parts = $activeSessionLine -replace '^\s+', '' -split '\s+'

        Write-Host "Parts from the last active session line: $parts"

        if ($parts.Length -gt 3) {
            $usernameIndex = $parts.IndexOf($username)
            if ($usernameIndex -gt -1 -and $usernameIndex + 1 -lt $parts.Length) {
                $sessionID = $parts[$usernameIndex + 1]
                Write-Host "Extracted session ID: $sessionID"
                return $sessionID
            }
        }

        Write-Host "Parts: $parts"
        Write-Host "Active session line: $activeSessionLine"
    } else {
        Write-Host "No active session found for the user $username."
    }
}

function ExecuteCommandInSession {
    param (
        [int]$SessionID,
        [string]$Command
    )
    $psExecPath = "C:\Windows\System32\PSTools\PsExec.exe"
    $execCommand = "$psExecPath -s -i $SessionID cmd.exe /c `"$Command`""
    Write-Output "Executing command in session {$SessionID}: $execCommand"
    Invoke-Expression $execCommand
}

$targetSessionID = Get-MostRecentSessionID

Write-Host "Session ID received: $targetSessionID"
if ($targetSessionID -ne $null) {
    ExecuteCommandInSession -SessionID $targetSessionID -Command $ExecutableCommand
} else {
    Write-Host "No recent RDP sessions found."
}
