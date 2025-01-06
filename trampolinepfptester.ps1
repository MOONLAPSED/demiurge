#------------------------------------------------------------------------------
# PowerShell Test Script for Echo Server
#------------------------------------------------------------------------------

# Create a new TCP client and connect to the server
try {
    $client = New-Object System.Net.Sockets.TcpClient("localhost", 8888)
    Write-Host "Connected to echo server at localhost:8888"
} catch {
    Write-Error "Failed to connect to echo server: $_"
    exit 1
}

# Ensure connection state
if (-not $client.Connected) {
    Write-Error "Failed to establish a connection."
    exit 1
}

# Create the stream, writer, and reader for communication
$stream = $client.GetStream()
$writer = New-Object System.IO.StreamWriter($stream)
$reader = New-Object System.IO.StreamReader($stream)
Write-Host "Connection state: $($client.Connected)"

# Send a message to the server
$message = "Hello Server"
try {
    $writer.WriteLine($message)
    $writer.Flush()
    Write-Host "Sent: $message"
} catch {
    Write-Error "Failed to send message: $_"
    $client.Close()
    exit 1
}

# Add timeout for reading response (in milliseconds)
$stream.ReadTimeout = 5000
try {
    $response = $reader.ReadLine()
    if ($response) {
        Write-Host "Received: $response"
    } else {
        Write-Warning "No response received (possibly empty response)."
    }
} catch {
    Write-Warning "No response received within the timeout period."
}

# Close the connection gracefully
Write-Host "Closing connection..."
try {
    $writer.Close()
    $reader.Close()
    $stream.Close()
    $client.Close()
    Write-Host "Connection closed successfully."
} catch {
    Write-Error "Error while closing connection: $_"
}
