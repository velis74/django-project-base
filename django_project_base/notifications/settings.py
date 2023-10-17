NOTIFICATIONS_SETTINGS = (
    {
        "name": "MAINTENANCE_NOTIFICATIONS_CACHE_TIMEOUT",
        "default": 30,
        "description": "Cache timeout for maintenance type notifications in UsersMaintenanceNotificationViewset",
    },
    {
        "name": "MAINTENANCE_NOTIFICATIONS_CACHE_KEY",
        "default": "current_maintenance_notifications",
        "description": "Maintenance notifications list cache key.",
    },
    {
        "name": "TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY",
        "default": 900,
        "description": "When list maintenance notifications api is called with current=true in query param, "
        "maintenance notification within range of now - TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY, "
        "now  + TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY is returned. Maintenance notification "
        "cannot be created if it overlaps with annother maintenance notification in buffer.",
    },
)
