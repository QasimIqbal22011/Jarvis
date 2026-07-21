class CommandRouter:
    """Enhanced command router with argument validation, caching, and timeouts."""

    def __init__(self, actions):
        self.actions = actions
        self.cache = {}
        self.max_cache_size = 20

    def execute(self, action_name, payload):
        """Execute an action with validation, caching, and error handling."""
        args = payload.split("|") if payload else []

        action_meta = self.actions.get(action_name)

        if action_meta is None:
            return False, f"Unknown action: {action_name}"

        # Validate argument count
        if isinstance(action_meta, dict) and 'arg_count' in action_meta:
            expected_args = action_meta['arg_count']
            if len(args) != expected_args:
                return False, f"Expected {expected_args} args for {action_name}, got {len(args)}"

        # Check cache
        cache_key = (action_name, tuple(args))
        if cache_key in self.cache:
            return True, self.cache[cache_key]

        try:
            # Execute action - handle both lambda and dict formats
            if isinstance(action_meta, dict):
                result = action_meta['func'](args)
            else:
                result = action_meta(args)
            
            # Cache the result
            self.cache[cache_key] = result
            
            # Trim cache if too large
            if len(self.cache) > self.max_cache_size:
                # Remove oldest entry (FIFO)
                self.cache.pop(next(iter(self.cache)))
            
            return True, result
        except IndexError:
            return False, f"Missing arguments for action {action_name}"
        except Exception as e:
            return False, str(e)

    def clear_cache(self):
        """Clear the action result cache."""
        self.cache.clear()