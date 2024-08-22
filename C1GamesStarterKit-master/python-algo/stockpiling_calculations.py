import math


# Case 1 means the structure (turrets in this case) can attack the mobile units, but the units cannot attack the structure
# NOTE TO SELF: For part 1, can't I just use total damage instead?
def case_1_1u_vs_1s(mobile_unit_health, turret_damage, frames_in_range) -> "tuple[bool, int]":
    """
    Single unit vs single structure. Structure can attack the mobile unit, but not the other way around
    Can the mobile unit survive?

    Returns:
    - Whether or not the unit will survive in this range
    - The amount of damage the unit will take
    """
    return frames_in_range < math.ceil(mobile_unit_health / float(turret_damage)), turret_damage * frames_in_range


def case_1_mu_vs_1s(num_mobile_units, mobile_unit_health, turret_damage, frames_in_range) -> "tuple[bool, int, int]":
    """
    Single unit vs multiple structures. Structures can attack the mobile unit, but not the other way around
    Can the mobile unit survive?

    Params:
    - num_mobile_units: The number of mobile units
    - mobile_unit_health: The health per mobile unit
    - turret_damage: The total damage from the turret summed up
    - frames_in_range: The number of frames in which the unit is in range of this much damage

    Returns:
    - Whether or not the unit will survive in this range
    - The amount of damage the unit will take
    """
    num_hits_to_kill_unit = math.ceil(mobile_unit_health / float(turret_damage))
    total_hits_needed = num_mobile_units * num_hits_to_kill_unit
    return frames_in_range < total_hits_needed, math.ceil((total_hits_needed - frames_in_range) / float(num_hits_to_kill_unit)), turret_damage * frames_in_range


def case_1_1u_vs_ms(mobile_unit_health, num_rturrets, num_uturrets, rturret_damage, uturret_damage, frames_in_range) -> "tuple[bool, int]":
    """
    Can the unit survive?
    """
    return frames_in_range < math.ceil(float(mobile_unit_health) / (num_rturrets*rturret_damage + num_uturrets*uturret_damage)), (num_rturrets*rturret_damage + num_uturrets*uturret_damage) * frames_in_range


def case_1_mu_vs_ms(num_mobile_units, mobile_unit_health, num_rturrets, num_uturrets, rturret_damage, uturret_damage, frames_in_range) -> "tuple[bool, int, int]":
    """
    Can the units survive?
    Note from Jane: I put the upgraded turrets to strike first because we always upgrade the turret before placing a regular one.
    I can't find a way to do this with quick maths... someone please let me know if you do!
    If speed is an issue, I know a faster way that gives an lower bound (the turrets will need AT LEAST this many frames to kill everyone)

    Failsafe: Send 14 scouts
    """
    turret_attack_sequence = [uturret_damage] * num_uturrets + [rturret_damage] * num_rturrets
    idx = 0
    damage_taken = 0
    num_units_remaining = 0
    num_frames_for_turrets_to_kill = 0
    for i in range(num_mobile_units):
        health = mobile_unit_health
        while health > 0:
            if idx == 0:
                num_frames_for_turrets_to_kill += 1
                if num_frames_for_turrets_to_kill == frames_in_range:
                    num_units_remaining = num_mobile_units - i
            health -= turret_attack_sequence[idx]
            damage_taken += turret_attack_sequence[idx]
            idx = 0 if idx == len(turret_attack_sequence) else idx + 1
    
    return frames_in_range < num_frames_for_turrets_to_kill, num_units_remaining, damage_taken


def case_1_mu_vs_ms_bounded(num_mobile_units, mobile_unit_health, num_rturrets, num_uturrets, rturret_damage, uturret_damage, frames_in_range) -> "tuple[bool, int, int]":
    """
    This is a faster version of the method above, but returns an estimate that is bounded, which means it might not be completely accurate but errs
    on the side of caution with a faster calculation.

    This method prioritizes the mobile units though, as it checks whether the units can get through the danger zone.
    """
    lower_bound = math.ceil(num_mobile_units * mobile_unit_health / (num_rturrets * rturret_damage + num_uturrets * uturret_damage))
    upper_bound = num_mobile_units * math.ceil(mobile_unit_health / (num_rturrets * rturret_damage + num_uturrets * uturret_damage))
    frames_in_range < math.ceil(float(mobile_unit_health) / (num_rturrets*rturret_damage + num_uturrets*uturret_damage)), (num_rturrets*rturret_damage + num_uturrets*uturret_damage) * frames_in_range


def case_1_total_damage(num_mobile_units, mobile_unit_health, total_damage_per_frame, frames_in_range) -> "tuple[bool, int, int]":
    """
    Kind of a "catch-all" function, we just calculate the total per frame by summing up the damages of all the turrets in range
    This method prioritizes the mobile units though, as it checks whether the units can get through the danger zone.

    Returns:
        - Whether or not the units will survive the onslaught. Errs on the side of caution
        - If they do, at least how many will survive?
        - How much damage will be taken in total?
    """
    lower_bound = math.ceil(num_mobile_units * mobile_unit_health / float(total_damage_per_frame))
    # upper_bound = num_mobile_units * math.ceil(mobile_unit_health / float(total_damage_per_frame))

    # Can we survive with the number of mobile units we have?
    can_survive_onslaught = frames_in_range < lower_bound

    # How many units will survive the onslaught?
    # (Total health - total damage) / health_per_unit, ceilinged
    num_units_survived = math.ceil((num_mobile_units * mobile_unit_health - frames_in_range * total_damage_per_frame) / float(mobile_unit_health))

    # How much damage will we take in total?
    damage_taken = frames_in_range * total_damage_per_frame
    
    return can_survive_onslaught, num_units_survived, damage_taken

# Case 3 means the units and structures (turrets) are in range to attack each other


def final(health_per_munit: int,
          total_health: int,
          structure_health: int,
          total_turret_damage: int,
          mobile_unit_damage: int,
          frames_in_range: int
) -> bool:
    """
    The overall "all-cases" function.

    Parameters:
    - health_per_munit: The health of each mobile unit
    - total_health: The total amount of health the mobile units have
    - structure_health: The health of the structure that mobile units are attacking. Not necessarily a turret,
                        we can fire on a wall while being attacked by turrets
    - total_turret_damage: The total amount of damage dealt by turrets per frame
    - mobile_unit_damage: The amount of damage dealth by a single mobile unit
    """
    
    # How many unit
    num_mobile_units = math.ceil(float(total_health) / health_per_munit)
    top_unit_health = total_health % health_per_munit if total_health % health_per_munit != 0 else health_per_munit


    # How many frames does it take to kill a single unit?
    num_frames_to_kill_full_health_unit = math.ceil(health_per_munit / float(total_turret_damage))
    num_frames_to_kill_top_unit = math.ceil(top_unit_health / float(total_turret_damage))
    

def case_2(num_mobile_units, mobile_unit_damage, structure_health, frames_in_range) -> "tuple[bool, int]":
    """
    Returns whether or not the structure was destroyed and how much damage was dealt
    """
    damage_dealt = num_mobile_units * mobile_unit_damage * frames_in_range
    structure_destroyed = structure_health <= damage_dealt
    return structure_destroyed, damage_dealt


def case_3_total_damage(num_mobile_units, mobile_unit_health, total_turret_damage, mobile_unit_damage, frames_in_range):
    pass

def case_3_1u_vs_1s(mobile_unit_health, 
                    mobile_unit_damage, 
                    turret_health, 
                    turret_damage, 
                    frames_in_range
                ) -> "tuple[bool, bool, int]":
    """
    Can the mobile unit survive? If so, how much damage will it take?

    Returns 
        - Whether or not the mobile unit survived
        - If the structure was successfully destroyed
        - The amount of damage taken (only useful and makes sense if alive)
    """

    # max number of frames the structure can survive in the unit's range
    fm = math.ceil(turret_health / float(mobile_unit_damage))

    # max number of frames the unit can survive in the structure's range
    fs = math.ceil(mobile_unit_health / float(turret_damage))

    survived = frames_in_range < fs
    turret_destroyed = frames_in_range >= fm
    damage_taken = frames_in_range * turret_damage

    return survived, turret_destroyed, damage_taken


def case_3_mu_vs_1s(num_mobile_units, mobile_unit_health, mobile_unit_damage, turret_health, turret_damage, frames_in_range) -> "tuple[bool, bool, int, int]":
    """
    The case where a wave of mobile units goes up against a single turret.
    Can the mobile units survive? If so, how many?

    Parameters:
    - num_mobile_units: The number of mobile units
    - mobile_unit_health: The health per mobile unit
    - mobile_unit_damage: The damage done by a single mobile unit
    - turret_health: How much health the turret has
    - turret_damage: The amount of damage done to us by the turret
    - frames_in_range: The number of frames we're in range

    Returns 
    - whether the units can survive
    - if the units can destroy the turret
    - The number of units that will survive
    - The total damage taken (only useful and makes sense if alive)
    """
    # How many frames does it take to kill a single unit?
    num_frames_to_kill_one_unit = math.ceil(mobile_unit_health / float(turret_damage)) 

    # How many units are killed every frame?
    kills_per_frame = turret_damage / float(mobile_unit_health)

    # Survival is determined by if the units could withstand getting hit frames_in_range times
    survived = frames_in_range < num_frames_to_kill_one_unit * num_mobile_units 

    # We determine the total damage we have done to the turret considering the gradual loss of units in the crossfire. The full calculation algorithm can be found in the documents
    total_damage_dealt_to_turret = num_frames_to_kill_one_unit * mobile_unit_damage * (num_mobile_units * frames_in_range - frames_in_range * (frames_in_range - 1) / 2.0)
    
    # If we have dealt enough damage, the turret is destroyed. IT IS POSSIBLE TO DESTROY THE TURRET AND NOT SURVIVE
    turret_destroyed = total_damage_dealt_to_turret >= turret_health

    # How much damage would we take? The sum of all the turret shots.
    damage_taken = turret_damage * frames_in_range

    # Based on the damage we've taken, we calculate the number of units that survived. If a unit has partial health, it's still technically alive
    num_units_survived = math.ceil((num_mobile_units * mobile_unit_health - damage_taken) / float(mobile_unit_health)) if survived else 0

    return survived, turret_destroyed, num_units_survived, damage_taken


def can_destroy_enemy() -> bool:
    """
    Returns a boolean on whether we have enough to destroy the enemy
    """
    pass


def weaker_enemy_side():
    """
    Return L, R, or None. If none, do not attack
    """
    pass