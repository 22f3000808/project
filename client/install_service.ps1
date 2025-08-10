$TaskName = "SysUtilAgent"
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$PSScriptRoot\main.py`" --background --interval 30"
$Trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -RunLevel Highest -Force
Write-Output "Scheduled task '$TaskName' created."
