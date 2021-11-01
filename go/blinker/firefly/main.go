package firefly

func CreateFireflies() {
	cacheCosSin()

	w, h := 3, 3
	cellSize := float32(100)
	NewWorld(w, h, cellSize)
}
