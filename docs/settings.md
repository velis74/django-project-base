# Settings options - quick overview


## DOCUMENTATION_DIRECTORY

```python
DOCUMENTATION_DIRECTORY = '/docs/build/'
```

Path for documentation directory.

## PROFILER_LONG_RUNNING_TASK_THRESHOLD

```python
PROFILER_LONG_RUNNING_TASK_THRESHOLD = 1000
```

Define treshold in ms for profiling long running tasks.


## MERGE_USERS_HANDLER

```python
MERGE_USERS_HANDLER = 'project.module.functions.function_to_execute'
```

If you choose to merge user accounts which belong to same user and you have MERGE_USERS_HANDLER setting defined, then
when user logs in with one of the account defined in accounts to merge group then function MERGE_USERS_HANDLER is executed 
which runs your logic for merging users.
Function is defined as def function(user, all_users, project). user argument is currently logged in user. all_users argument is 
a comma separated string of user pks which will be merged.
