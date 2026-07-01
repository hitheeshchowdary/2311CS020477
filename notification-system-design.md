## Stage 1
Assume a front-end developer colleague has asked you for REST API design, contract and structure to display notifications to the users when they are logged in. Identify the core actions that the notification platform should support. Now, you have to present the REST API endpoints along with their JSON request, response, and headers structures using an appropriate format. Define clear and consistent endpoints for each action, using predictable naming conventions, and design JSON schemas with essential fields. Also, you are to design a mechanism for real-time notifications.

### Endpoints
- `GET /notifications?studentId={id}` → fetch notifications
- `POST /notifications` → create notification
- `PATCH /notifications/{id}` → mark as read

### Headers
```http
Authorization: Bearer <token>
Content-Type: application/json
{
  "id": 123,
  "studentId": 1042,
  "message": "Placement drive tomorrow",
  "isRead": false,
  "createdAt": "2026-07-01T09:00:00Z",
  "notificationType": "Placement"
}


## Stage 2
On the basis of the APIs and contract you created earlier, you now have to store the same reliably. Which persistent storage (DB) do you suggest and explain your choice. Write the applicable DB schema. What problems could arise as the data volume increases? How would you solve such problems? Write SQL or NoSQL queries based on your DB schema and the REST APIs that you designed in Stage 1.

### Suggested DB
- **PostgreSQL**: reliable, supports indexing, handles large datasets, widely used in production.

### Schema
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    studentId INT NOT NULL,
    message TEXT NOT NULL,
    isRead BOOLEAN DEFAULT FALSE,
    notificationType VARCHAR(20),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


## Stage 3
Optimize queries based on the schema.

### Original Query
```sql
SELECT * FROM notifications
WHERE studentId = 1042 AND isRead = false
ORDER BY createdAt DESC;
 
//fix 
CREATE INDEX idx_notifications_student_read 
ON notifications(studentId, isRead, createdAt DESC);

//example
SELECT * FROM notifications
WHERE notificationType = 'Placement'
AND createdAt >= NOW() - INTERVAL '7 days';


## Stage 4
Performance considerations.

### Problem
- Fetching notifications on every page load causes high database load and slow response times.
- As the number of users grows, repeated queries for the same data waste resources.

### Solutions
- **Caching**: Store recent notifications in Redis or Memcached to reduce repeated DB hits.
- **Pagination**: Return notifications in pages (e.g., 20 at a time) instead of all at once.
- **Push model**: Use WebSockets or Server-Sent Events to push new notifications directly to clients, avoiding constant polling.

### Trade-offs
- Caching adds complexity and requires invalidation strategies.
- Pagination improves performance but requires front-end handling.
- Push model ensures instant updates but requires persistent connections and more server resources.


## Stage 5
Redesign the "Notify All" pseudocode.

### Issues
- Sequential loop → slow when many students.
- No retry mechanism for failures.
- Database writes and email sending tightly coupled.

### Improved Design
Use a **message queue** (RabbitMQ/Kafka) to decouple tasks and allow retries.

### Pseudocode
```python
def notify_all(student_ids, message):
    for student_id in student_ids:
        enqueue_job("send_email", student_id, message)
        enqueue_job("save_to_db", student_id, message)
        enqueue_job("push_to_app", student_id, message)


## Stage 6
Priority Inbox implementation.

### Requirement
- Show top 10 unread notifications by priority (Placement > Result > Event) and recency.

### Approach
- Assign numeric priority values to each notification type.
- Use a heap or sorting to select the top 10 based on priority and timestamp.
- Ensure only unread notifications are considered.

### Python Code
```python
from heapq import nlargest

priority_map = {"Placement": 3, "Result": 2, "Event": 1}

def fetch_notifications():
    # Mocked notifications if API is protected
    return [
        {"id": 1, "notificationType": "Placement", "message": "Drive tomorrow", "isRead": False, "createdAt": "2026-07-01T09:00:00Z"},
        {"id": 2, "notificationType": "Result", "message": "Exam results out", "isRead": False, "createdAt": "2026-07-01T08:00:00Z"},
        {"id": 3, "notificationType": "Event", "message": "Workshop today", "isRead": False, "createdAt": "2026-07-01T07:00:00Z"},
    ]

def priority_score(notification):
    return (priority_map.get(notification["notificationType"], 0), notification["createdAt"])

def get_top_notifications(n=10):
    notifications = fetch_notifications()
    unread = [n for n in notifications if not n["isRead"]]
    top = nlargest(n, unread, key=priority_score)
    return top

if __name__ == "__main__":
    top10 = get_top_notifications()
    for n in top10:
        print(f"{n['notificationType']} - {n['message']} ({n['createdAt']})")
