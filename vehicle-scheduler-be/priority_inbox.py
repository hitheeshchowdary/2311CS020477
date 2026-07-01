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
