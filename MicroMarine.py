from datetime import date, datetime
from random import *
from time import time

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
from sc2.ids.ability_id import AbilityId

from gobo import ZergBot


class MicroMarine(BotAI):
    async def on_step(self, iteration):

        
        # setup
        if iteration == 0:
            self.go_all_in = False

            self.cc = self.townhalls[0]
            
            self.cc.train(UnitTypeId.SCV)
            
        if self.units(UnitTypeId.MARINE):
            self.marine_leader = self.units(UnitTypeId.MARINE).closest_to(self.enemy_start_locations[0])

        if  self.units(UnitTypeId.SCV):
            self.scv_leader = self.units(UnitTypeId.SCV).closest_to(self.enemy_start_locations[0])
       

        #grouping / splitting / stutter stepping

        #target fire

        #marines in range
        #marines under threat

       

        # Attack with all Marines
        # Group Marines within range of each other

        # for marine in self.units(UnitTypeId.MARINE):
        #    nearby_marines = self.units(UnitTypeId.MARINE).closer_than(0.8*marine.ground_range, marine)
        #    if len(nearby_marines) < 7 :
        #        marine.move(nearby_marines.center)

        # strategic rally state
        if self.go_all_in == False:
            self.rally = self.main_base_ramp.top_center
                 

        #define enemy units into classes for target priority

        enemy_units = self.enemy_units.exclude_type(
            [UnitTypeId.EGG, UnitTypeId.LARVA, UnitTypeId.DRONE, UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.OVERLORD])

        melee_units = self.enemy_units(
            [UnitTypeId.ZEALOT, UnitTypeId.ZERGLING, UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.DRONE])
        
        enemy_workers = self.enemy_units(
            [UnitTypeId.DRONE, UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.MULE])

        enemy_structures = self.enemy_structures


        if enemy_units:
            #shoot at the lowest health enemy in range
            for marine in self.units(UnitTypeId.MARINE):
                banelings_nearby = (self.enemy_units(UnitTypeId.BANELING).filter(lambda x: x.distance_to(marine) <= 4))
                if enemy_units.in_attack_range_of(marine) and banelings_nearby:
                    marine.target = sorted(enemy_units.in_attack_range_of(marine), key=lambda u: u.health + u.shield)[0]
                elif enemy_workers.in_attack_range_of(marine):
                    marine.target = sorted(enemy_workers.in_attack_range_of(marine), key=lambda u: u.health + u.shield)[0]
                else:
                    marine.target = self.enemy_start_locations[0]

            #scvs are blockers
            for scv in self.starting_scvs:
                scv.target = enemy_units.closest_to(scv)

        elif enemy_workers:
            for marine in self.units(UnitTypeId.MARINE):
                if enemy_workers.in_attack_range_of(marine):
                    marine.target = sorted(enemy_workers.in_attack_range_of(marine), key=lambda u: u.health + u.shield)[0]
                else:
                    marine.target = enemy_workers.closest_to(marine)

            for scv in self.starting_scvs:
                scv.target = enemy_workers.closest_to(scv)

        elif enemy_structures:
            for marine in self.units(UnitTypeId.MARINE):
                marine.target = enemy_structures.closest_to(marine)
            for scv in self.starting_scvs:
                scv.target = enemy_structures.closest_to(scv)

        elif self.supply_army > 9 and self.go_all_in == False:
            self.go_all_in = True
            self.rally = self.enemy_start_locations[0]
            self.starting_scvs = self.units(UnitTypeId.SCV).take(16)
            # Select 12 SCVs to attack with the Marines
            for scv in self.starting_scvs:
                scv.attack(self.enemy_start_locations[0])
            for marine in self.units(UnitTypeId.MARINE):
                marine.move(self.main_base_ramp.top_center)

        if self.go_all_in:
            for scv in self.starting_scvs:
                #direction = scv.position - self.marine_leader.position
                #direction = direction.normalized
                #scv.move(direction)
                #scv.attack(self.enemy_start_locations[0])
                if scv.distance_to(self.scv_leader) > 14:
                    scv.move(self.scv_leader)
                else:
                    scv.attack(self.enemy_start_locations[0])

            for marine in self.units(UnitTypeId.MARINE):
                if marine.distance_to(self.marine_leader) > 14:
                    marine.move(self.marine_leader)
                else:
                    marine.attack(self.enemy_start_locations[0])


        if self.go_all_in and self.supply_used < 28:
            self.go_all_in = False
            self.rally = self.main_base_ramp.top_center
            for marine in self.units(UnitTypeId.MARINE):
                marine.attack(self.units(UnitTypeId.MARINE).center)

           
            
            


        # Micro Marines:
        



        for marine in self.units(UnitTypeId.MARINE):

            # Find all banelings within 3 distance of each marine
            banelings_nearby = self.enemy_units(UnitTypeId.BANELING).filter(lambda x: x.distance_to(marine) <= 4)
            melee_attackers_nearby = melee_units.filter(lambda x: x.distance_to(marine) < 2)
            # If there are banelings nearby, move the marine directly away from them
            if banelings_nearby:
                # Calculate the direction to move in by subtracting the marine's position from the baneling's position
                direction = marine.position - banelings_nearby[0].position
                # Normalize the direction to get a unit vector
                direction = direction.normalized
                # Move the marine in the opposite direction of the banelings
                marine.move(marine.position + direction)
                
            #retreat from melee attackers
            
            elif melee_attackers_nearby:
                direction = marine.position - melee_attackers_nearby[0].position
                direction = direction.normalized
                marine.move(marine.position + direction)


        #attack the tank, stutter step towards ranged enemies and away from melee  
        #priority buildings, supply, production, cleanup
            elif enemy_units:
        
                closest_enemy = enemy_units.closest_to(marine)

                if marine.distance_to(closest_enemy) >= marine.ground_range-2 and marine.distance_to(closest_enemy) < marine.ground_range+2:
                    marine.attack(marine.target)
                    marine.move(closest_enemy.position)
                    
                else:
                    marine.attack(marine.target)
                for scv in self.starting_scvs:
                    scv.attack(scv.target)

            elif enemy_workers:
                marine.attack(marine.target)
            elif self.units(UnitTypeId.MARINE).amount > 16 and enemy_structures:
                marine.attack(marine.target)
            
        if self.units(UnitTypeId.MARINE):
            if self.units(UnitTypeId.MARINE).closer_than(5, self.marine_leader).amount < 3:
                self.marine_leader.move(self.main_base_ramp.top_center)
            if self.marine_leader.distance_to(self.enemy_start_locations[0]) - 1 < self.scv_leader.distance_to(self.enemy_start_locations[0]):
                self.marine_leader.move(self.main_base_ramp.top_center)
            if self.scv_leader.distance_to(self.enemy_start_locations[0]) < self.marine_leader.distance_to(self.enemy_start_locations[0]) and self.go_all_in:
                if self.starting_scvs.closer_than(6, self.scv_leader).amount < 2:
                    self.scv_leader.move(self.main_base_ramp.top_center)

        
        #depots 
        depot_placement_positions: FrozenSet[Point2] = self.main_base_ramp.corner_depots

        depots: Units = self.structures.of_type(
            {UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED})
        if depots:
            depot_placement_positions: Set[Point2] = {
                d
                for d in depot_placement_positions if depots.closest_distance_to(d) > 1
            }


        #raise depots when enemy is near, otherwise keep lowered
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
 # Build 1st Supply Depot
        if depots.amount + self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0 and len(depot_placement_positions) > 0:

            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                target_depot_location: Point2 = depot_placement_positions.pop()
                await self.build(UnitTypeId.SUPPLYDEPOT, target_depot_location)

        # Build the first Barracks in the wall
        if self.structures(UnitTypeId.BARRACKS).amount + self.already_pending(UnitTypeId.BARRACKS) < 1 and self.can_afford(UnitTypeId.BARRACKS):
            await self.build(UnitTypeId.BARRACKS, self.main_base_ramp.barracks_in_middle)

        # Build the second Barracks to complete the wall
        if self.townhalls:
            if self.structures(UnitTypeId.BARRACKS).amount + self.already_pending(UnitTypeId.BARRACKS) < 2 and self.can_afford(UnitTypeId.BARRACKS):
                if not self.units(UnitTypeId.BARRACKS).closer_than(1.0, self.main_base_ramp.top_center).exists:
                    await self.build(UnitTypeId.BARRACKS, near=self.main_base_ramp.top_center)

        # Build a third Barracks near the townhall
        if self.already_pending(UnitTypeId.BARRACKS) == 2 and self.can_afford(UnitTypeId.BARRACKS):
            await self.build(UnitTypeId.BARRACKS, near=self.cc)
        
        # Build SCVs as needed
        if self.structures(UnitTypeId.BARRACKS).amount == 3 and self.units(UnitTypeId.SCV).amount < 22 and self.supply_left > 1:
            for ccs in self.structures(UnitTypeId.COMMANDCENTER).ready.idle:
                if self.can_afford(UnitTypeId.SCV):
                    ccs.train(UnitTypeId.SCV)

        # Train Marines constantly on all available Barracks
        for rax in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if self.can_afford(UnitTypeId.MARINE):
                rax.train(UnitTypeId.MARINE)

        # Send idle SCVs to harvest minerals
        if self.townhalls:
            for scv in self.units(UnitTypeId.SCV).idle:
                scv.gather(self.mineral_field.closest_to(self.cc))

        # build 2nd  supply depot in the wall
        if self.structures(UnitTypeId.BARRACKS).amount == 3 and len(depot_placement_positions) > 0 and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:

            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                target_depot_location: Point2 = depot_placement_positions.pop()
                await self.build(UnitTypeId.SUPPLYDEPOT, target_depot_location)

        #build  additional depots
        if self.townhalls:
            if depots.amount >= 2 and self.supply_left < 5 and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    await self.build(UnitTypeId.SUPPLYDEPOT, near=self.cc)

        # Build a fourth Barracks near the wall
        if self.townhalls:
            if self.structures(UnitTypeId.BARRACKS).amount >= 3 and self.structures(UnitTypeId.BARRACKS).amount < 5 and self.minerals > 300 and self.already_pending(UnitTypeId.BARRACKS) == 0:
                await self.build(UnitTypeId.BARRACKS, near=self.main_base_ramp.top_center)




def main():
    rand=random()*10000
    randstr=str(rand)

    run_game(
        maps.get("CatalystLE"), [
        Bot(Race.Terran, MicroMarine()),
        Bot(Race.Zerg, ZergBot()),
        # Bot(Race.Protoss, CannonRushBot(), name="CheeseCannon")
        #Computer(Race.Random, Difficulty.VeryHard)
        #Human(Race.Terran)
], realtime=False, save_replay_as="gptbot"+randstr+".SC2Replay",)

if __name__ == "__main__":
    main()
