# Tactix
A work-stealing actor framework for Python built on Tokio.r.

The easiest way to understand how Tactix works is think: 
#### asyncio + threading + actors => tactix

Unlike asyncio tactix will not be stopped or be interrupted by blocking tasks,
instead if a particular worker thread is blocking the other threads will steal
the work off of the blocked thread until it is released again. 

This does mean you can use regular blocking calls like time.sleep(n) and not
fear blocking the whole loop but note this will still affect the loop if more
than `n` blocking tasks are running where `n` is the amount of logical CPU cores.

## Example
```py

```

