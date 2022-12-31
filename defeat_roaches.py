import tensorflow as tf


from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL  # beacon/minerals
_PLAYER_ENEMY = features.PlayerRelative.ENEMY

FUNCTIONS = actions.FUNCTIONS
RAW_FUNCTIONS = actions.RAW_FUNCTIONS


def _xy_locs(mask):
  """Mask should be a set of bools from comparison with a feature layer."""
  y, x = mask.nonzero()
  return list(zip(x, y))

def q_network(state_size, action_size):
  inputs = tf.keras.layers.Input(shape=(state_size,))
  x = tf.keras.layers.Dense(64, activation='relu')(inputs)
  x = tf.keras.layers.Dense(64, activation='relu')(x)
  outputs = tf.keras.layers.Dense(action_size)(x)
  model = tf.keras.Model(inputs=inputs, outputs=outputs)
  return model

class DefeatRoaches(base_agent.BaseAgent):
  """An agent specifically for solving the DefeatRoaches map."""

  def __init__(self, state_size, action_size):
    self.state_size = state_size
    self.action_size = action_size
    self.q_network = q_network(state_size, action_size)  # function approximator for Q-values

  def step(self, obs):
    super(DefeatRoaches, self).step(obs)
    if FUNCTIONS.Attack_screen.id in obs.observation.available_actions:
      player_relative = obs.observation.feature_screen.player_relative
      roaches = _xy_locs(player_relative == _PLAYER_ENEMY)
      if not roaches:
        return FUNCTIONS.no_op()

      # Extract state features
      state = obs.observation.feature_screen[...]

      # Preprocess state for the neural network
      state = tf.convert_to_tensor(state, dtype=tf.float32)
      state = tf.expand_dims(state, 0)  # add batch dimension

      # Select action with highest Q-value
      q_values = self.q_network(state)
      action = np.argmax(q_values)

      return FUNCTIONS.Attack_screen("now", roaches[0])