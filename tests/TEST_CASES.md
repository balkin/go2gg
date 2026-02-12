# Test Cases

## Timeouts
- Creating a client without supplying a custom timeout should apply the default timeout values.
- Supplying explicit timeout parameters should override the defaults.

## Retries (disabled by default)
- When retry_count is 0, a 5xx response should raise an APIError without retrying.

## Retries (enabled)
- When retry_count is 1 and the first response is 500 then 200, the request should succeed.
- When retry_count is 2 and retry_backoff is enabled, the delays should grow exponentially.
- Network errors (e.g., connection error) should be retried when retry_count > 0.
