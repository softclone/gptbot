from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId

class WallOffBot(BotAI):
    async def on_step(self, iteration):

        #setup
        #if iteration == 1:
        if self.townhalls:
            cc = self.townhalls[0]
      

        depot_placement_positions: FrozenSet[Point2] = self.main_base_ramp.corner_depots
      

        depots: Units = self.structures.of_type({UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED})
        if depots:
            depot_placement_positions: Set[Point2] = {
                d
                for d in depot_placement_positions if depots.closest_distance_to(d) > 1
            }

        for depo in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depo) < 15:
                    break
            else:
                depo(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

        for depo in self.structures(UnitTypeId.SUPPLYDEPOTLOWERED).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depo) < 10:
                    depo(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
                    break

        #Build SCV
        if iteration == 1:
             cc.train(UnitTypeId.SCV)

        # Build 1st Supply Depot
        if depots.amount + self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0 and len(depot_placement_positions) > 0:
          
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                target_depot_location: Point2 = depot_placement_positions.pop()
                await self.build(UnitTypeId.SUPPLYDEPOT, target_depot_location)

        # Build SCVs as needed
        if self.structures(UnitTypeId.BARRACKS).amount == 3 and self.units(UnitTypeId.SCV).amount < 22 and self.supply_left > 1:
            for ccs in self.structures(UnitTypeId.COMMANDCENTER).ready.idle:
                if self.can_afford(UnitTypeId.SCV):
                    ccs.train(UnitTypeId.SCV)

        # Build the first Barracks in the wall
        if self.structures(UnitTypeId.BARRACKS).amount + self.already_pending(UnitTypeId.BARRACKS) < 1 and self.can_afford(UnitTypeId.BARRACKS):
            await self.build(UnitTypeId.BARRACKS, self.main_base_ramp.barracks_in_middle)

        # Build the second Barracks to complete the wall
        if self.structures(UnitTypeId.BARRACKS).amount + self.already_pending(UnitTypeId.BARRACKS) < 2 and self.can_afford(UnitTypeId.BARRACKS):
            if not self.units(UnitTypeId.BARRACKS).closer_than(1.0, self.main_base_ramp.top_center).exists:
                await self.build(UnitTypeId.BARRACKS, near=cc)

        # Build a third Barracks near the townhall
        if self.already_pending(UnitTypeId.BARRACKS) == 2 and self.can_afford(UnitTypeId.BARRACKS):
            await self.build(UnitTypeId.BARRACKS, near=cc)

        # Set the rally point for all Barracks to the top of the ramp
        for rax in self.structures(UnitTypeId.BARRACKS):
            rax.smart(self.main_base_ramp.top_center)

        # Train Marines constantly on all available Barracks
        for rax in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if self.can_afford(UnitTypeId.MARINE):
                rax.train(UnitTypeId.MARINE)

        # Send idle SCVs to harvest minerals
        if self.townhalls:
            for scv in self.units(UnitTypeId.SCV).idle:
                scv.gather(self.mineral_field.closest_to(cc))
        
        # build more supply depots
        if self.structures(UnitTypeId.BARRACKS).amount == 3 and len(depot_placement_positions) > 0 and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
          
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                target_depot_location: Point2 = depot_placement_positions.pop()
                await self.build(UnitTypeId.SUPPLYDEPOT, target_depot_location)

        if self.townhalls:
            if depots.amount >= 2 and self.supply_left < 5 and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    await self.build(UnitTypeId.SUPPLYDEPOT, near=cc)

        # Build a fourth Barracks near the townhall
        if self.townhalls:
            if self.structures(UnitTypeId.BARRACKS).amount >= 3 and self.minerals > 250 and self.already_pending(UnitTypeId.BARRACKS) == 0:
                await self.build(UnitTypeId.BARRACKS, near=cc)

        # Attack with all Marines 
        # Attack with all Marines 
        
        # Select a target to attack
        
        enemy_units = self.enemy_units
        enemy_structures = self.enemy_structures
        if enemy_units:
            for marine in self.units(UnitTypeId.MARINE):
                target = enemy_units.closest_to(marine)
        elif enemy_structures:
            for marine in self.units(UnitTypeId.MARINE):
                target = enemy_structures.closest_to(marine)
        elif self.supply_army > 9:
            target = self.enemy_start_locations[0]
            
        # Move and attack with Marines
        if target:
            for marine in self.units(UnitTypeId.MARINE):
                # Stutter-step to move closer to the target if it is out of range
                if marine.distance_to(target) > marine.ground_range:
                    marine.move(target.position)
                
                else:
                    if enemy_units:
                        for marine in self.units(UnitTypeId.MARINE):
                            closest_enemy = enemy_units.closest_to(marine)
                            if marine.distance_to(closest_enemy) >= marine.ground_range-2:
                                marine.move(marine.position)
                                marine.attack(closest_enemy)
                            else:
                                marine.attack(closest_enemy)
                    elif enemy_structures:
                        for marine in self.units(UnitTypeId.MARINE):
                            target = enemy_structures.closest_to(marine)
                            marine.attack(target)
                    
            # and SCVs in control group 1
            #for scv in self.units(UnitTypeId.SCV):
                #   if scv.is_carrying_minerals:
                #      scv.tags
                # if scv.stay_home == 1:
                #    continue
                #scv.attack(target)

def main():
    run_game(
        maps.get("CatalystLE"), [
        Bot(Race.Terran, WallOffBot()),
        Bot(Race.Terran, WallOffBot())
], realtime=True)

if __name__ == "__main__":
    main()