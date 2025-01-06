# Establish a TCP connection to the server
$client = New-Object System.Net.Sockets.TcpClient("localhost", 8869)
$stream = $client.GetStream()
$writer = New-Object System.IO.StreamWriter($stream)
$reader = New-Object System.IO.StreamReader($stream)

Write-Host "Connected to echo server at localhost:8888"
Write-Host "Connection state: " $client.Connected

# Send message to the server
$message = "Hello from PowerShell"
$writer.WriteLine($message)
$writer.Flush()
Write-Host "Sent: $message"

# Set a read timeout for the response
$stream.ReadTimeout = 5000
try {
    $response = $reader.ReadLine()
    Write-Host "Received: $response"
} catch {
    Write-Host "No response received within timeout period"
}

Write-Host "Closing connection..."
$writer.Close()
$reader.Close()
$stream.Close()
$client.Close()
Write-Host "Connection closed"
