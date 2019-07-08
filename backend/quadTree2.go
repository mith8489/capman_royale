package main

import (
	"fmt"
	//	"time"
	//	"math/rand"
	"bufio"
	"os"
	"strings"
	"sync"
)

// Position contains current position and facing.
type Position struct {
	X      int
	Y      int
	Facing Direction
}

//Axis aligned bounding box. Center position represents middle of sprite.
type BoundingBox struct {
	Center     Position
	HalfHeight int
	HalfWidth  int
	Mutex      sync.Mutex
}

/*----------Intersection methods for bounding boxes----------*/

// Boolean to check if position is within BoundingBox
func (bBox *BoundingBox) containsPoint(point Position) bool {
	topLeft := bBox.getCorners()[0]
	bottomRight := bBox.getCorners()[1]

	return ((point.X >= topLeft.X && point.X <= bottomRight.X) && (point.Y >= topLeft.Y && point.Y <= bottomRight.Y))
}

// Returns topleft and bottom right of BoundingBox
func (bBox *BoundingBox) getCorners() [2]Position {
	topLeft := Position{X: (bBox.Center.X - bBox.HalfWidth), Y: (bBox.Center.Y - bBox.HalfHeight)}
	bottomRight := Position{X: (bBox.Center.X + bBox.HalfWidth), Y: (bBox.Center.Y + bBox.HalfHeight)}
	coordArray := [2]Position{topLeft, bottomRight}
	return coordArray
}

// Returns smallest int of x and y.
func min(x, y int) int {
	if x > y {
		return y
	}
	return x
}

// returns largest int of x and y.
func max(x, y int) int {
	if x < y {
		return y
	}
	return x
}

// Boolean to check if bounding boxes intersect.
func (boxOne *BoundingBox) intersectsBox(boxTwo BoundingBox) bool {
	boxOneCorners := boxOne.getCorners()
	boxTwoCorners := boxTwo.getCorners()

	intersectRectX1 := max(boxOneCorners[0].X, boxTwoCorners[0].X)
	intersectRectY1 := max(boxOneCorners[0].Y, boxTwoCorners[0].Y)
	intersectRectX2 := min(boxOneCorners[1].X, boxTwoCorners[1].X)
	intersectRectY2 := min(boxOneCorners[1].Y, boxTwoCorners[1].Y)

	return intersectRectX1 < intersectRectX2 && intersectRectY1 < intersectRectY2
}

/*----------------------------------------------------------*/

// struct for QuadTree
type QuadTree struct {

	//Boundary of the tree
	Boundary BoundingBox

	//Overlapping bounding boxes
	OverlapBoxes []*BoundingBox

	//Children
	NorthWest *QuadTree
	NorthEast *QuadTree
	SouthWest *QuadTree
	SouthEast *QuadTree

	IsWall bool //Only set in lowest level tree
}

func (qt *QuadTree) insert(bBox *BoundingBox) {
	if qt.Boundary.HalfHeight * 2 == TILE_SIZE {
		qt.OverlapBoxes = append(qt.OverlapBoxes, bBox)
	}
	else {
		qt.NorthWest = &getChildNode(-1, -1, parentCenter, childHalfSide)
		qt.NorthEast = &getChildNode(1, -1, parentCenter, childHalfSide)
		qt.SouthWest = &getChildNode(-1, 1, parentCenter, childHalfSide)
		qt.SouthEast = &getChildNode(1, 1, parentCenter, childHalfSide)
		if qt.NorthWest.intersectsBox(bBox) {
			qt.NorthWest.insert(bBox)
		}
		if qt.NorthEast.intersectsBox(bBox) {
			qt.NorthEast.insert(bBox)
		}
		if qt.SouthWest.intersectsBox(bBox) {
			qt.SouthWest.insert(bBox)
		}
		if qt.SouthEast.intersectsBox(bBox) {
			qt.SouthEast.insert(bBox)
		}
	}
}

// returns childnode
// xAdjust and yAdjust must be 1 or -1
func getChildNode(xAdjust int, yAdjust int, parentCenter Position, halfSide int) QuadTree {
	centerX := parentCenter.X + (xAdjust * halfSide)
	centerY := parentCenter.Y + (yAdjust * halfSide)
	center := Position{X: centerX, Y: centerY}
	childNode := QuadTree{Boundary: BoundingBox{Center: center, HalfHeight: halfSide, HalfWidth: halfSide}}
	return childNode
}


// returns tile containing position of quadtree
func (qt *QuadTree) GetTileOfPoint(point Position) *QuadTree {
	if !qt.hasPoint(point) {
		fmt.Println("Not found!")
		return nil
	} else {
		return qt.getTileOfPointAux(point)
	}
}

// aux for getTileOfPointAux
func (qt *QuadTree) getTileOfPointAux(point Position) *QuadTree {
	if qt.NorthWest != nil {
		if qt.NorthWest.hasPoint(point) {
			return qt.NorthWest.getTileOfPointAux(point)
		}
		if qt.NorthEast.hasPoint(point) {
			return qt.NorthEast.getTileOfPointAux(point)
		}
		if qt.SouthWest.hasPoint(point) {
			return qt.SouthWest.getTileOfPointAux(point)
		}
		if qt.SouthEast.hasPoint(point) {
			return qt.SouthEast.getTileOfPointAux(point)
		}
	}
	return qt
}

// hasBox is a boolean checking if boxes is in quadtree
func (qt *QuadTree) hasBox(bBox BoundingBox) bool {
	return qt.Boundary.intersectsBox(bBox)
}

// boolean to check if position is in quadtree.
func (qt *QuadTree) hasPoint(point Position) bool {
	return qt.Boundary.containsPoint(point)
}

// finds overlaps
func (qt *QuadTree) findOverlaps(bBox BoundingBox) []QuadTree {
	matchingQuads := make([]QuadTree, 0)
	return qt.findOverlapsAux(bBox, matchingQuads)
}

// aux for findOverlaps
func (qt *QuadTree) findOverlapsAux(bBox BoundingBox, accumulator []QuadTree) []QuadTree {
	if qt.NorthWest != nil {

		if qt.NorthWest.hasBox(bBox) {
			accumulator = qt.NorthWest.findOverlapsAux(bBox, accumulator)
		}
		if qt.NorthEast.hasBox(bBox) {
			accumulator = qt.NorthEast.findOverlapsAux(bBox, accumulator)
		}
		if qt.SouthWest.hasBox(bBox) {
			accumulator = qt.SouthWest.findOverlapsAux(bBox, accumulator)
		}
		if qt.SouthEast.hasBox(bBox) {
			accumulator = qt.SouthEast.findOverlapsAux(bBox, accumulator)
		}

	} else {
		accumulator = append(accumulator, *qt)
	}

	return accumulator
}

// checks if object is in a wall, to check for illegal move.
func (qt *QuadTree) IsObjectOnWall(bBox BoundingBox) bool {
	overlappingNodes := qt.findOverlaps(bBox)
	for i := 0; i < len(overlappingNodes); i++ {
		if overlappingNodes[i].IsWall {
			return true
		}
	}
	return false
}

// sets wall tiles.
func (qt *QuadTree) setWallTiles() {
	mapFile, err := os.Open("mapFile.txt")
	if err != nil {
		panic(err)
	}
	defer mapFile.Close()

	fmt.Print("\n  Map:\n  ")
	reader := bufio.NewReader(mapFile)
	for i := 0; i < MAP_TILE_HEIGHT; i++ {
		line, _ := reader.ReadString('\n')
		lineCells := strings.Fields(line)
		for j := 0; j < MAP_TILE_WIDTH; j++ {
			cellCenter := Position{X: (j + 1) * TILE_SIZE, Y: (i + 1) * TILE_SIZE}
			if lineCells[j] == "*" {
				wallBox = BoundingBox{Center: cellCenter, HalfHeight: TILE_SIZE / 2, HalfWidth: TILE_SIZE / 2}
				qt.insert(wallBox)
				fmt.Print("██")
			} else {
				fmt.Print("  ")
			}
		}
		fmt.Print(" \n  ")
	}
	fmt.Print(" \n")
}

// prints a map to console.
func drawMap() {
	fmt.Print("\n  Map:\n  ")
	for i := 0; i < MAP_TILE_HEIGHT; i++ {
		for j := 0; j < MAP_TILE_WIDTH; j++ {
			matchingQuadrant := GameMap.GetTileOfPoint(Position{X: (j + 1) * TILE_SIZE, Y: (i + 1) * TILE_SIZE})
			hasPlayer := false
			players.Mutex.Lock()
			for _, player := range players.Players {
				playerQuadrant := GameMap.GetTileOfPoint(player.Boundary.Center)
				if playerQuadrant.Boundary.Center == matchingQuadrant.Boundary.Center {
					fmt.Print("PC")
					hasPlayer = true
				}
			}
			players.Mutex.Unlock()
			if matchingQuadrant.IsWall {
				fmt.Print("██")
			} else if !hasPlayer {
				fmt.Print("  ")
			}
		}
		fmt.Print(" \n  ")
	}
	//	fmt.Println(" \n")
}
