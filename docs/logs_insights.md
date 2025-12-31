# Logs Insights Queries

This file contains sample CloudWatch Logs Insights queries for the MasterProject application.

---

## 1. Count errors in app logs
Show the number of errors (500, ERROR, error) per minute:

```sql
fields @timestamp, @message
| filter @message like /500|ERROR|error/
| stats count() as ErrorCount by bin(1m)
```

## 2. Recent app requests
Get the last 20 HTTP requests to the application:

```sql 
fields @timestamp, @message
| filter @message like /GET/
| sort @timestamp desc
| limit 20
```

## 3. Slow responses (>150ms)
Find requests that took longer than 150ms:

```sql
fields @timestamp, @message
| filter @message like /GET/ and @message like /ms/
| parse @message "* * * * * * * * * * *" as ip, user, method, path, protocol, status, size, time
| filter time > 0.15
| sort time desc
| limit 20
```