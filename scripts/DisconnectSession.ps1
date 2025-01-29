param (
    [string]$TargetIP
)

function Get-ProcessIDByIP {
    param (
        [string]$IP
    )
    # Get all established TCP connections
    $connections = Get-NetTCPConnection -State Established
    # Filter connections where the remote address matches the IP
    $filteredConnections = $connections | Where-Object { $_.RemoteAddress -eq $IP }
    
    # Extract the PID directly and cleanly
    $targetRDPClientPIDs = $filteredConnections | ForEach-Object {
        $_.OwningProcess
    }

    # Assuming there might be multiple, unique PIDs, let's pick the first one
    $targetRDPClientPID = $targetRDPClientPIDs | Select-Object -Unique | Select-Object -First 1

    # Check and convert to integer explicitly
    if ($targetRDPClientPID -and $targetRDPClientPID -is [int]) {
        return $targetRDPClientPID
    } elseif ($targetRDPClientPID -and $targetRDPClientPID -isnot [int]) {
        try {
            return [int]$targetRDPClientPID
        } catch {
            Write-Output "Failed to convert PID to integer: $targetRDPClientPID"
            return $null
        }
    } else {
        return $null
    }
}


function Stop-ProcessByPID {
    param (
        [int]$ProcessID
    )
    Write-Output "Attempting to stop process ID: $ProcessID"
    try {
        $process = Get-Process -Id $ProcessID
        $process | Stop-Process -Force
        Write-Output "Process $ProcessID has been terminated."
    } catch {
        Write-Output "Failed to terminate process $ProcessID. Error: $_"
    }
}

if ($TargetIP) {
    $targetRDPClientPID = Get-ProcessIDByIP -IP $TargetIP
    if ($targetRDPClientPID) {
        Write-Output "Found PID $targetRDPClientPID for IP $TargetIP"
        Stop-ProcessByPID -ProcessID $targetRDPClientPID
    } else {
        Write-Output "No connection found for IP $TargetIP"
    }
} else {
    Write-Output "No Target IP provided."
}
