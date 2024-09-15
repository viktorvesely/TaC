class ThiefActions:
    @staticmethod
    def select_target(thief):
        def action():
            target = thief.find_closest_citizen()
            if target:
                thief.target = target
                return True
            return False
        return action

    @staticmethod
    def close_distance(thief):
        def action():
            if thief.target:
                thief.move_towards(thief.target.position)
                if thief.is_within_range(thief.target):
                    return True
            return False
        return action

    @staticmethod
    def scan_environment(thief):
        def action():
            return thief.check_risks()
        return action

    @staticmethod
    def proceed_with_theft(thief):
        def action():
            if thief.scan_environment():
                return True
            return False
        return action

    @staticmethod
    def commit_theft(thief):
        def action():
            return thief.successful_theft()
        return action

    @staticmethod
    def theft_success(thief):
        def action():
            thief.increase_motivation()
            thief.target = None
        return action

    @staticmethod
    def theft_fail(thief):
        def action():
            thief.decrease_motivation()
            thief.target = None
        return action

    @staticmethod
    def abort_theft(thief):
        def action():
            return False
        return action

