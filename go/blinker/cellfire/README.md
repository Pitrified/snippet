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

Random communications between cells and fireflies.

Cache the entire distance comm decision as `[][]bool`:
even with radius 200, you need only 40kB.
You could then use proper L2 distance easily.

MAYBE copy the Fireflies map to Nudgeable map,
then a firefly blinks, delete her from Nudgeable.
When computing the distances, use only Nudgeable,
so the loops get shorter and there is no need to access f.nudgeable.


NOTE: all this might fire simultaneously, not just in this step
the first blink could nudge some of them and make them blink in step
eg deadlines f1 1010 f2 1020, clock 1050
both blink, but if f2 is in range with f1, f2 should blink at 1010
MAYBE do a minimal distance check only between these?
but also the neighboring ones...
The point is that if they nudge each other in this simulation step,
there is actually a NudgeAmount of time elapsed
eg deadlines f1 1010 f2 1020 f3 1015, clock 1050, all in range
if f3 is the first parsed in the map, f2 is nudged by her (f1 is not)
and we have to wait f1-f2 for the correct firing of f2 at 1010
so maybe we could keep computing all pairs?
at this point a cache of distances might be useful.

Send the nudge to the neighbors also on the corner cell.

# Implementation details

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

If the nudge leads to a blink,
the deadline should be pushed only to match the nudger's deadline.
We should leave the nudged firefly in the list to check,
and if another firefly is in range and can nudge further
(no more than the max of course)
we can.

Hierarchy:

* **World**:
    * Maintains a toroidal grid of cells.
    * Coordinates the evolution of the sistem:
        * Tick the clock.
        * Blink.
* **Cell**:
    * Maintains a map of fireflies inside it.
    * When blinking all, `wgClockTick` marks that there is still work left.
        When the `blinkQueue` is empty, call `Done` on the workgroup,
        and mark the cell as idling.
        When *other* cells put more fireflies in the queue,
        check for idling, and if so call `Add(1)` on the wg.
* **Firefly**:
    * Maintains info on the fireflies:
        * Position: `x,y float32`
        * Orientation: in degrees (`int16`),
            precompute the 360 values for cos/sin `float32` in the `[0, 360)` range.

* Use Manhattan distance, no one cares.

# TODOs

The fireflies must stay with `nudgeable` set to false for more than one round!
At least `200ms`.
