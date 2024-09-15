class CitizenActions:
    @staticmethod
    def roaming(citizen):
        def action():
            citizen.position += citizen.random_movement()
        return action

   