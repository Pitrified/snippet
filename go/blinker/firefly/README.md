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

The fireflies *do* move with an internal `ticker` they listen to,
but one of the channels the firefly is listening to is `doRender`:
inside the firefly will wait on `doRenderDone`.
The cell rendering also listens on `doRender` (from the world):
* No need to lock the map
    (the cell rendering channel is one in the `Listen` select,
    so `Enter/Leave` do not fire).
* Some fireflies might be waiting on `Enter/Leave` ch, remember that.
* Some fireflies might be in limbo: left one but still not joined the other.
    (MAYBE: the world has a channel `chCellChange`
    where the fireflies sends the request to change cells:
    the world tells to a cell that a firefly wants to move and the destination,
    and the cell coordinates with the neighbor)
    (MAYBE: the firefly computes the new cell and when sending the `Leave`
    message the cell takes care of contacting the neighbor)

A whole lot of deadlock risks:
* A firefly is trying to blink (and needs to communicate with a cell)
* The cell is trying to move the fireflies (and need to coomunicate with them)
* Alternatively, a firefly is trying to move and needs to communicate
    with a cell or with the world.

The world might keep a queue of `changeCell` requests,
to free as fast as he can the fireflies.

One goroutine per firefly is probably madness.

Lets work on the [cellfire](../cellfire) version :D

# TODOs
