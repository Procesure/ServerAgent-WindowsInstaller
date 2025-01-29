param (
    [string]$ExecutableCommand  # Command to run, including the full path to the executable and any arguments
)

function Get-MostRecentSessionID {
    # Retrieve the output of 'query user', skipping the header
    $queryOutput = query user | Select-Object -Skip 1

    # Get the last entry from the output
    $lastLine = $queryOutput[-1].Trim()

    # Split the last line by whitespace to extract parts
    $parts = $lastLine -split '\s+'

    # The session ID should be the third element in the parts array
    $sessionID = $parts[2]

    # Return the session ID
    return $sessionID
}

function ExecuteCommandInSession {
    param (
        [int]$SessionID,
        [string]$Command
    )
    $psExecPath = "C:\Windows\System32\PSTools\PsExec.exe"
    $execCommand = "$psExecPath -s -i $SessionID cmd.exe /c `"$Command`""
    Write-Output "Executing command in session ${SessionID}: $execCommand"
    Invoke-Expression $execCommand

}

$mostRecentSession = Get-MostRecentSessionID
Write-Output $mostRecentSession
if ($mostRecentSession) {
    Write-Output "Most recent session ID is $($mostRecentSession)"
    ExecuteCommandInSession -SessionID $mostRecentSession -Command $ExecutableCommand
} else {
    Write-Output "No recent RDP sessions found."
}
