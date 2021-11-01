package firefly

import (
	"fmt"
	"math"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCacheCosSin(t *testing.T) {
	cacheCosSin()

	casesCos := []struct {
		o    uint8
		want float32
	}{
		{0, 1},
		{15, float32(math.Sqrt(3) / 2)},
		{30, 0.5},
		{45, 0},
	}
	for _, c := range casesCos {
		assert.InDelta(t, cos[c.o], c.want, 1e-6, fmt.Sprintf("Failed %+v", c))
	}

	casesSin := []struct {
		o    uint8
		want float32
	}{
		{0, 0},
		{15, 0.5},
		{30, float32(math.Sqrt(3) / 2)},
		{45, 1},
	}
	for _, c := range casesSin {
		assert.InDelta(t, sin[c.o], c.want, 1e-6, fmt.Sprintf("Failed %+v", c))
	}

}
