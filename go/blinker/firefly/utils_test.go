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
		{60, -0.5},
		{75, -float32(math.Sqrt(3) / 2)},
		{90, -1},
		{105, -float32(math.Sqrt(3) / 2)},
		{120, -0.5},
		{135, 0},
		{150, 0.5},
		{165, float32(math.Sqrt(3) / 2)},
	}
	for _, c := range casesCos {
		assert.InDelta(t, cos[c.o], c.want, 1e-6, fmt.Sprintf("Failed %+v, had %+v", c, cos[c.o]))
	}

	casesSin := []struct {
		o    uint8
		want float32
	}{
		{0, 0},
		{15, 0.5},
		{30, float32(math.Sqrt(3) / 2)},
		{45, 1},
		{60, float32(math.Sqrt(3) / 2)},
		{75, 0.5},
		{90, 0},
		{105, -0.5},
		{120, -float32(math.Sqrt(3) / 2)},
		{135, -1},
		{150, -float32(math.Sqrt(3) / 2)},
		{165, -0.5},
	}
	for _, c := range casesSin {
		assert.InDelta(t, sin[c.o], c.want, 1e-6, fmt.Sprintf("Failed %+v", c))
	}

}

func TestValidateOri(t *testing.T) {
	casesCos := []struct {
		in   uint8
		want uint8
	}{
		{0, 0},
		{15, 15},
		{179, 179},
		{180, 180},
	}
	for _, c := range casesCos {
		assert.Equal(t, c.in, c.want, fmt.Sprintf("Failed %+v", c))
	}
}
