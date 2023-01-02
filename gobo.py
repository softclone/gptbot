import random
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId
#from wallOffBot2 import WallOffBot2


class ZergBot(BotAI):

    # def build_queen(self, hatch):


    # def group_queens(self):


    def select_target(self):
        if self.enemy_structures:
            return random.choice(self.enemy_structures).position
        return self.enemy_start_locations[0]


    async def on_step(self, iteration):

        larvae: Units = self.larva
        queens: Units = self.units(UnitTypeId.QUEEN)
        forces: Units = self.units.of_type({UnitTypeId.ZERGLING, UnitTypeId.BANELING})

        if self.townhalls:
            hq = self.townhalls[0]
            hq.smart(self.main_base_ramp.top_center)
            if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
                if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                    await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))
            if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
                if not self.units(UnitTypeId.QUEEN) and hq.is_idle:
                    if self.can_afford(UnitTypeId.QUEEN):
                        hq.train(UnitTypeId.QUEEN)
                if self.units(UnitTypeId.QUEEN).amount < 2 and hq.is_idle and self.minerals > 300:
                        hq.train(UnitTypeId.QUEEN)
            for queen in queens:
                # The following checks if the inject ability is in the queen abilitys - basically it checks if we have enough energy and if the ability is off-cooldown
                # abilities = await self.get_available_abilities(queen)
                # if AbilityId.EFFECT_INJECTLARVA in abilities:
                if queen.energy >= 25:
                    queen(AbilityId.EFFECT_INJECTLARVA, hq)


        if self.supply_left < 2 and not self.already_pending(UnitTypeId.OVERLORD):
            if larvae and self.can_afford(UnitTypeId.OVERLORD):
                larvae.random.train(UnitTypeId.OVERLORD)
                return
        
        if self.units(UnitTypeId.DRONE).amount < 15:
            if larvae and self.can_afford(UnitTypeId.DRONE) :
                larvae.random.train(UnitTypeId.DRONE)
                return

        #if self.structures(UnitTypeId.SPAWNINGPOOL).amount == 1 and self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) < 1:
         #   if self.can_afford(UnitTypeId.EXTRACTOR):
          #      drone: Unit = self.workers.random
           #     target: Unit = self.vespene_geyser.closest_to(drone.position)
            #    drone.build_gas(target)
             #   return

        # Build pool



        # Saturate gas
        for a in self.gas_buildings:
            if a.assigned_harvesters < a.ideal_harvesters:
                w: Units = self.workers.closer_than(10, a)
                if w:
                    w.random.gather(a)

        if self.gas_buildings.amount == 0 and not self.already_pending(UnitTypeId.EXTRACTOR) and self.already_pending(UnitTypeId.SPAWNINGPOOL):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                drone: Unit = self.workers.random
                target: Unit = self.vespene_geyser.closest_to(drone.position)
                drone.build_gas(target)
                return

        if self.gas_buildings.amount == 1 and not self.already_pending(UnitTypeId.EXTRACTOR) and self.supply_army > 1:
            if self.can_afford(UnitTypeId.EXTRACTOR):
                drone: Unit = self.workers.random
                target: Unit = self.vespene_geyser.closest_to(drone.position)
                drone.build_gas(target)
                return

        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
                    
            if self.structures(UnitTypeId.BANELINGNEST).amount + self.already_pending(UnitTypeId.BANELINGNEST) < 1:
                if self.can_afford(UnitTypeId.BANELINGNEST):
                    await self.build(UnitTypeId.BANELINGNEST, near=hq.position.towards(self.game_info.map_center, 5))
        
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED
                                                  ) == 0 and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
                self.structures(UnitTypeId.SPAWNINGPOOL)[0].research(UpgradeId.ZERGLINGMOVEMENTSPEED)

        for z in self.units(UnitTypeId.ZERGLING):
            if self.can_afford(UnitTypeId.BANELING) and self.units(UnitTypeId.BANELING).amount < self.units(UnitTypeId.ZERGLING).amount:
                z(AbilityId.MORPHZERGLINGTOBANELING_BANELING)
                z.attack(self.main_base_ramp.top_center)
                return

        if larvae and self.can_afford(UnitTypeId.ZERGLING):
                larvae.random.train(UnitTypeId.ZERGLING)
                return

        if iteration % 50 == 0 and forces.amount > 30:
            for unit in forces:
                unit.attack(self.select_target())

        

        
        # Attack with all Marines 
        # if self.supply_army > 12:
        #     # Select a target to attack
        #     enemy_units = self.enemy_units
        #     enemy_structures = self.enemy_structures
        #     if enemy_units:
        #         target = enemy_units.closest_to(self.start_location)
        #     elif enemy_structures:
        #         target = enemy_structures.closest_to(self.start_location)
        #     else:
        #         target = self.enemy_start_locations[0]
        #     # Move and attack with Marines
        #     for marine in self.units(UnitTypeId.MARINE):
        #         # Stutter-step to move closer to the target if it is out of range
        #         if marine.distance_to(target) > marine.ground_range:
        #             marine.move(target.position)
                
        #         else:
        #             if enemy_units:
        #                 closest_enemy = enemy_units.closest_to(marine)
        #                 if marine.distance_to(closest_enemy) >= marine.ground_range-1:
        #                     marine.move(marine.position)
                    
        #                     marine.attack(closest_enemy)
                    
            # and SCVs in control group 1
            #for scv in self.units(UnitTypeId.SCV):
             #   if scv.is_carrying_minerals:
              #      scv.tags
               # if scv.stay_home == 1:
                #    continue
                #scv.attack(target)

def main():
    rand=random.random()*10000
    randstr=str(rand)
    run_game(
        maps.get("CatalystLE"), [
        Bot(Race.Zerg, ZergBot()),
        #Bot(Race.Terran, WallOffBot2()),
        #Computer(Race.Terran, Difficulty.CheatInsane)
], realtime=False, save_replay_as="gobo"+randstr+".SC2Replay",)

if __name__ == "__main__":
    main()