# Background Processing  
  
## Overview  
  
Background processing enables the WhatsApp Bot to perform long-running tasks without blocking the main application thread.  
This is particularly important for operations like fetching large batches of messages or generating summaries.  
  
## Implementation  
  
The application uses a threaded approach for background processing:  
  
```python  
class BackgroundTask(threading.Thread):  
    def __init__(self, task_function, args=None, kwargs=None, callback=None):  
        super().__init__()  
        self.task_function = task_function  
        self.args = args or ()  
        self.kwargs = kwargs or {}  
        self.callback = callback  
        self.result = None  
        self.error = None  
        self.completed = False  
        self.daemon = True  # Allow the program to exit even if the thread is running  
  
    def run(self):  
        try:  
            self.result = self.task_function(*self.args, **self.kwargs)  
            if self.callback:  
                self.callback(self.result)  
        except Exception as e:  
            self.error = e  
        finally:  
            self.completed = True  
```  
  
## Progress Reporting  
  
Implement progress reporting to provide feedback for long-running tasks:  
  
```python  
def task_with_progress(total_items):  
    progress = {"current": 0, "total": total_items, "status": "in_progress"}  
  
    def update_progress(increment=1, status=None):  
        progress["current"] += increment  
        if status:  
            progress["status"] = status  
        # Calculate percentage  
        percentage = int((progress["current"] / progress["total"]) * 100)  
        print(f"Progress: {percentage}% - {progress['current']}/{progress['total']}")  
  
    def task_function(items):  
        for item in items:  
            # Process item  
            process_item(item)  
            # Update progress  
            update_progress()  
        update_progress(status="completed")  
  
    return task_function, update_progress  
``` 
## Example Usage  
  
Here's how to use the background processing in your application:  
  
```python  
# Example: Generating a summary in the background  
def generate_summary_with_progress(messages, progress_callback=None):  
    total = len(messages)  
    processed = 0  
  
    def update_progress():  
        nonlocal processed  
        processed += 1  
        if progress_callback:  
            progress_percentage = (processed / total) * 100  
            progress_callback(progress_percentage)  
  
    summary = ""  
    for message in messages:  
        # Process message  
        summary += process_message(message)  
        update_progress()  
  
    return summary  
  
# Start the process in background  
def start_summary_generation():  
    def on_complete(result):  
        print("Summary generation completed!")  
        display_summary(result)  
  
    def progress_handler(percentage):  
        print(f"Summary generation: {percentage:.1f}% complete")  
  
    messages = fetch_messages_from_database()  
    task = BackgroundTask(  
        task_function=generate_summary_with_progress,  
        args=(messages,),  
        kwargs={"progress_callback": progress_handler},  
        callback=on_complete  
    )  
    task.start()  
    return task  # Return the task object for status checking  
```  
  
## Best Practices  
  
1. **Avoid Shared State**: Minimize shared state between threads to prevent race conditions and synchronization issues.  
  
2. **Proper Resource Cleanup**: Ensure resources are properly cleaned up when background tasks complete.  
  
3. **Error Handling**: Implement robust error handling in background tasks and propagate errors back to the main application.  
  
4. **Task Timeouts**: Implement timeouts for long-running tasks to prevent them from running indefinitely.  
  
5. **Task Prioritization**: Consider implementing a priority queue for background tasks if different tasks have different importance levels.  
  
6. **State Management**: Provide a way to check the status of background tasks (running, completed, failed).  
  
7. **Limiting Concurrent Tasks**: Implement a task queue with a maximum number of concurrent tasks to prevent resource exhaustion.  
  
## Task Queue Implementation  
  
For more complex applications, consider implementing a task queue:  
  
```python  
class TaskQueue:  
    def __init__(self, max_concurrent=5):  
        self.queue = queue.Queue()  
        self.active_tasks = []  
        self.max_concurrent = max_concurrent  
        self.lock = threading.Lock()  
        self._stop_event = threading.Event()  
        self.worker_thread = threading.Thread(target=self._worker)  
        self.worker_thread.daemon = True  
        self.worker_thread.start()  
  
    def add_task(self, task_function, args=None, kwargs=None, callback=None):  
        """Add a task to the queue"""  
        task = BackgroundTask(task_function, args, kwargs, callback)  
        self.queue.put(task)  
        return task  
  
    def _worker(self):  
        """Worker thread that processes the queue"""  
        while not self._stop_event.is_set():  
            try:  
                # Remove completed tasks  
                with self.lock:  
                    self.active_tasks = [t for t in self.active_tasks if not t.completed]  
  
                # Start new tasks if we're under the limit  
