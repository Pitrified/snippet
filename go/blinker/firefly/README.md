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

Hierarchy:

* **World**:
    * Maintains a toroidal grid of cells.
    * Can send a `doStep` signal to all of them.
        Mostly for sanity in updating the fireflies positions all at once,
        and computing reasonable distances.
        I don't like it.
        Each firefly should have an internal timer and do her thing,
        moving around `fpsMove` times per second.
    * Can send a `pause` signal?
* **Cell**:
    * Maintains a map of fireflies inside it:
        When receiving a request to `exit` and `enter` cells from a firefly,
        adding/removing from a map should be fast.
    * Can send a `doStep` signal to all of them.
* **Firefly**:
    * Maintains info on the fireflies:
        * Position: `x,y float32`
        * Orientation: in degrees (`uint8`),
            precompute the 180 values for cos/sin `float32`.
            180 so it fits in a `uint8` :)
        * Speed: `s float32`? Later on if needed.
    * When blinking, the signal is sent to the occupied cell.
    * Knows the shape of the cells in the world:
        can send a request to `exit` and `enter` cells.
    * After blinking, the firefly cannot be nudged for a while:
        start a `time.After`,
        and `select` on it and the channel where nudges are received.

* Maybe stop the `f.nudgeable` at the start of `doBlink`.

* Use Manhattan distance, no one cares.

# TODOs
