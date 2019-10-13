# The Chosen One - Multi-Agent Reinforcement Learning with Autocurricula
![Chosen One Main Pic](https://user-images.githubusercontent.com/27071473/66710764-65894500-edb1-11e9-9088-525f526655fb.png)

# Introduction Video - Animator vs Animation by Alan Becker
https://www.youtube.com/watch?v=npTC6b5-yvM&t=60s

# Contributions
* PyGame environment, consisting Chosen One (agent), Gun and Bullets
* Multi-agent Reinforcement Learning Training, consisting Chosen One (agent) and Generator (Gun)

# Demonstration
## Agent learnt to camp at a corner:
![camp_clip](https://user-images.githubusercontent.com/27071473/66710997-db8fab00-edb5-11e9-9824-9de7ab1532c4.gif)

## Agent learnt to dodge Gun bullets:
![demo](https://user-images.githubusercontent.com/27071473/66710966-42f92b00-edb5-11e9-92ed-e92cd9c3304f.gif)

# Method
* Trained over 1K epochs of 500 timesteps.
* Chosen One
  * Model: 5 hidden layers, 100 hidden channels
  * Reward function: +1 if surviving, -50 if hit
  * Discount factor (g): 0.995
  * Exploration policy: Epsilon-greedy (e = 0.3)
  * Experience replay: Buffer (size = 10^6)
* Game Environment
  * State dimension: (25,)
    * Agent: jumps, xpos, ypos, touchingObst, gravityCurrent
    * 5 Entities: x, y, speed, angle
  * Action space: (3,)
    * Agent: left, right, jump
    * Generator: weapon_type, x, y, angle

# References
* DDQN - [Deep Reinforcement Learning with Double Q-learning](https://arxiv.org/abs/1509.06461)
* ChainerRL - [Deep Reinforcement Learning Library](https://chainerrl.readthedocs.io/en/latest/index.html)
* PyGame - [Python Game Library](https://www.pygame.org/docs/)
