# Firefly simulator

Small scale interactions can lead to large scale organization,
which is super cool.
Veritasium has an excellent
[video](https://www.youtube.com/watch?v=t-_VPRCtiUg)
about this phenomenon.

A simulation of the environment is
[available](https://ncase.me/fireflies/),
and it is even
[open source](https://github.com/ncase/fireflies).
But the size of the swarm can only reach 500.
Rookie numbers.

We want to simulate 1.000.000+ fireflies.

# IDEAs

No fancy timers to make the fireflies blink.
We keep an internal `us` clock, and advance it as needed.
(Possibly as parallel as possible.)
Also move, and change cells for the fireflies.
When the clock is ahead of the internal deadline: blink.
To blink, add the firefly to a blink queue.
To ALL the blink queues of the neighbors!
    Only if the current firefly is near the border!
Block the nudgeability of the firefly as soon as you put her in the queue.
While processing the queues, also check the fireflies in the neighboring cells.
    Only if the current firefly is near the border!

Hierarchy:

* **World**:
    * Maintains a toroidal grid of cells.
    * Coordinates the evolution of the sistem:
        * Tick the clock.
        * Blink.
* **Cell**:
    * Maintains a map of fireflies inside it.
* **Firefly**:
    * Maintains info on the fireflies:
        * Position: `x,y float32`
        * Orientation: in degrees (`int16`),
            precompute the 360 values for cos/sin `float32`.

* Use Manhattan distance, no one cares.

# TODOs
