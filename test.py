import sc2
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer

class MyBot(BotAI):
    async def on_step(self, iteration: int):
        print(f"This is my bot in iteration {iteration}!")

sc2.run_game(
    sc2.maps.get("AcropolisLE"),
    [Bot(sc2.Race.Zerg, MyBot()), Computer(sc2.Race.Zerg, sc2.Difficulty.Hard)],
    realtime=False,
)