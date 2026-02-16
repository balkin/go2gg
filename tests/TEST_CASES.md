# Test Cases

## Timeouts
- Creating a client without supplying a custom timeout should apply the default timeout values.
- Supplying explicit timeout parameters should override the defaults.
- Closing a client that uses an externally managed session should not close the external session.

## Retries (disabled by default)
- When retry_count is 0, a 5xx response should raise an APIError without retrying.

## Retries (enabled)
- When retry_count is 1 and the first response is 500 then 200, the request should succeed.
- When retry_count is 2 and retry_backoff is enabled, the delays should grow exponentially.
- When retry_backoff is disabled and retry_delay is positive, each retry should use the same fixed delay.
- Network errors (e.g., connection error) should be retried when retry_count > 0.

## Error Handling
- A non-JSON API error response body should fall back to the plain-text message.
- If retries continue until the loop is exhausted, the client should raise the final "Request failed after retries." RequestError.

## Model Parsing
- LinkStats.from_dict should ignore aggregate fields when they are not lists.
