from datetime import date, datetime
from random import *
from time import time

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
from sc2.ids.ability_id import AbilityId


class WallOffBot2(BotAI):
    async def on_step(self, iteration):

        if self.townhalls:
            cc = self.townhalls[0]
        # setup
        if iteration == 0:
            self.go_all_in = False
            cc.train(UnitTypeId.SCV)
            self.scvs = self.units(UnitTypeId.SCV).take(12)
        if iteration == 3330:
            self.scvs = self.units(UnitTypeId.SCV).take(20)

        if self.townhalls:
            cc = self.townhalls[0]

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

        # Build SCVs as needed
        if self.structures(UnitTypeId.BARRACKS).amount == 3 and self.units(UnitTypeId.SCV).amount < 22 and self.supply_left > 1:
            for ccs in self.structures(UnitTypeId.COMMANDCENTER).ready.idle:
                if self.can_afford(UnitTypeId.SCV):
                    ccs.train(UnitTypeId.SCV)

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

        # Build a fourth Barracks near the wall
        if self.townhalls:
            if self.structures(UnitTypeId.BARRACKS).amount >= 3 and self.structures(UnitTypeId.BARRACKS).amount < 5 and self.minerals > 250 and self.already_pending(UnitTypeId.BARRACKS) == 0:
                await self.build(UnitTypeId.BARRACKS, near=self.main_base_ramp.top_center)

        # Attack with all Marines
        # Attack with all Marines
        # Group Marines within range of each other

        # for marine in self.units(UnitTypeId.MARINE):
        #    nearby_marines = self.units(UnitTypeId.MARINE).closer_than(0.8*marine.ground_range, marine)
        #    if len(nearby_marines) < 7 :
        #        marine.move(nearby_marines.center)

        # Select a target to attack
        if self.go_all_in == False:
            self.target = self.main_base_ramp.top_center

        enemy_units = self.enemy_units.exclude_type(
            [UnitTypeId.EGG, UnitTypeId.LARVA, UnitTypeId.DRONE, UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.OVERLORD])
        enemy_workers = self.enemy_units.exclude_type(
            [UnitTypeId.EGG, UnitTypeId.LARVA, UnitTypeId.OVERLORD])

        enemy_structures = self.enemy_structures
        if enemy_units:
            for marine in self.units(UnitTypeId.MARINE):
                self.target = enemy_units.closest_to(marine)
            for scv in self.scvs:
                self.target = enemy_units.closest_to(scv)
        elif enemy_workers:
            for marine in self.units(UnitTypeId.MARINE):
                self.target = enemy_workers.closest_to(marine)
            for scv in self.scvs:
                self.target = enemy_workers.closest_to(scv)
        elif enemy_structures:
            for marine in self.units(UnitTypeId.MARINE):
                self.target = enemy_structures.closest_to(marine)
        elif self.supply_army > 9 and self.go_all_in == False:
            self.target = self.enemy_start_locations[0]
            self.go_all_in = True
            self.marine_leader = self.units(UnitTypeId.MARINE).closest_to(
                self.enemy_start_locations[0])
            for scv in self.scvs:
                scv.move(self.marine_leader)
                scv.attack(self.target)
            # Select 10 SCVs to attack with the Marines

            # Move the SCVs to the front of the army

        # Move and attack with Marines
        if self.target:

            for marine in self.units(UnitTypeId.MARINE):
            # Stutter-step to move closer to the target if it is out of range
                if marine.distance_to(self.target) > marine.ground_range:
                    marine.move(self.target.position)

            if enemy_units:
                self.marine_leader = self.units(UnitTypeId.MARINE).closest_to(
                    self.enemy_start_locations[0])
                for marine in self.units(UnitTypeId.MARINE):
                    closest_enemy = enemy_units.closest_to(marine)
                    if marine.distance_to(closest_enemy) >= marine.ground_range-2 and marine.distance_to(closest_enemy) < marine.ground_range+2:
                        marine.move(closest_enemy.position)
                        marine.attack(closest_enemy)
                    else:
                        marine.attack(closest_enemy)
                for scv in self.scvs:
                    scv.attack(enemy_units.closest_to(self.marine_leader))
                # elif enemy_structures:
                #   for marine in self.units(UnitTypeId.MARINE):
                #      self.target = enemy_structures.closest_to(marine)
                #     marine.attack(self.target)
                # elif self.target == self.enemy_start_locations[0]:
                #   for scv in self.scvs:
                #      scv.move(self.marine_leader)
                #     scv.attack(self.closest_to(self.marine_leader)


def main():
    rand=random()*10000
    randstr=str(rand)

    run_game(
        maps.get("CatalystLE"), [
        Bot(Race.Terran, WallOffBot2()),
        #Bot(Race.Terran, WallOffBot2()),
        # Bot(Race.Protoss, CannonRushBot(), name="CheeseCannon")
        Computer(Race.Random, Difficulty.CheatInsane)
        #Human(Race.Terran)
], realtime=False, save_replay_as="gptbot"+randstr+".SC2Replay",)

if __name__ == "__main__":
    main()
