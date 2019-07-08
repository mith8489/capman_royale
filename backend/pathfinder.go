
package main

type AStarTile struct {
	Tile   *QuadTree
	GScore int
	HScore int
}

func getAdjTiles(currentTile *AStarTile) []*AStarTile {
	currentCenter := currentTile.Tile.Boundary.Center
	adjTiles := make([]*AStarTile, 4, 4)
	northTilePos := Position{X: currentCenter.X, Y: currentCenter.Y - TILE_SIZE}
	adjTiles[0] = &AStarTile{Tile: GameMap.GetTileOfPoint(northTilePos), GScore: currentTile.GScore + 1}
	eastTilePos := Position{X: currentCenter.X + TILE_SIZE, Y: currentCenter.Y}
	adjTiles[1] = &AStarTile{Tile: GameMap.GetTileOfPoint(eastTilePos), GScore: currentTile.GScore + 1}
	southTilePos := Position{X: currentCenter.X, Y: currentCenter.Y + TILE_SIZE}
	adjTiles[2] = &AStarTile{Tile: GameMap.GetTileOfPoint(southTilePos), GScore: currentTile.GScore + 1}
	westTilePos := Position{X: currentCenter.X - TILE_SIZE, Y: currentCenter.Y}
	adjTiles[3] = &AStarTile{Tile: GameMap.GetTileOfPoint(westTilePos), GScore: currentTile.GScore + 1}

	return adjTiles
}

func filterIntoOpenList(adjTiles []*AStarTile, closedList []*AStarTile, openList []*AStarTile) {
	for i := 0; i < len(adjTiles); i++ {
		if !GameMap.IsObjectOnWall(adjTiles[i].Tile.Boundary) && !isTileInSlice(adjTiles[i], closedList) {
			openList = append(openList, adjTiles[i])
		}
	}
}

func isTileInSlice(tileA *AStarTile, slice []*AStarTile) bool {
    for _, tileB := range slice {
        if tileA == tileB {
            return true
        }
    }
    return false
}