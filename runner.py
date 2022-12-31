from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units

# Import the DefeatRoaches agent
from  defeat_roaches import DefeatRoaches

def main():
  # Create an instance of the DefeatRoaches agent
  agent = DefeatRoaches(state_size=512, action_size=16)

  # Create the SC2 environment
  try:
    with sc2_env.SC2Env(
        map_name="DefeatRoaches",
        players=[sc2_env.Agent(sc2_env.Race.terran)],
        agent_interface_format=features.AgentInterfaceFormat(
            feature_dimensions=features.Dimensions(screen=84, minimap=64),
            use_feature_units=True),
        step_mul=16,
        game_steps_per_episode=0,
        visualize=True) as env:

      # Run the SC2 environment with the DefeatRoaches agent
      run_loop([agent], env)
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  main()