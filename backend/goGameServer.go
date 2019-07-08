// The package which contains goGameServer.go and quadTree.go
// goGameServer.go handles all of the requests
// quadTree.go handles allowed positions and movement
package main

import (
	"fmt"
	"net"
	"sync"
)

var GameIsRunning bool
var GameMutex sync.Mutex

var GameMap QuadTree

// map size constants
var TILE_SIZE int
var HALF_TILE_SIZE int
var MAP_WIDTH int
var MAP_HEIGHT int
var HALF_MAP_WIDTH int
var HALF_MAP_HEIGHT int
var MAP_TILE_WIDTH int
var MAP_TILE_HEIGHT int

// Sets map constants to intial defined values.
func setMapConstants() {
	TILE_SIZE = 32 // width and height of one map tile, in pixels (this is the smallest side size of a QuadTree node)
	HALF_TILE_SIZE = TILE_SIZE / 2
	MAP_WIDTH = 1024 // width of the map, in pixels
	MAP_HEIGHT = 768 // height of the map, in pixels
	HALF_MAP_WIDTH = MAP_WIDTH / 2
	HALF_MAP_HEIGHT = MAP_HEIGHT / 2
	MAP_TILE_WIDTH = MAP_WIDTH / TILE_SIZE   // number of tiles in each tile row
	MAP_TILE_HEIGHT = MAP_HEIGHT / TILE_SIZE // number of tiles in each tile column
}

var PLAYER_PIXEL_SIZE int
var BOT_PIXEL_SIZE int
var PLAYER_MVMT_SPEED int
var BOT_MVMT_SPEED int
var PLAYER_HIT_POINTS int
var BOT_HIT_POINTS int
var BOT_ATTACK_POWER int
var BULLET_PIXEL_SIZE int
var BULLET_MVMT_SPEED int
var BULLET_DMG int

func setPlayerBotConstants() {
	PLAYER_PIXEL_SIZE = 48
	BOT_PIXEL_SIZE = 66
	PLAYER_MVMT_SPEED = 4
	BOT_MVMT_SPEED = 2
	PLAYER_HIT_POINTS = 100
	BOT_HIT_POINTS = 100
	BOT_ATTACK_POWER = 25

	BULLET_PIXEL_SIZE = 8
	BULLET_MVMT_SPEED = 8
	BULLET_DMG = 75
}

type PlayerMap struct {
	Players map[string]*Player
	Mutex   sync.Mutex
}

// players contains pointers to all the Player objects in the game, mapped
// as values with their own names as keys.
var players PlayerMap

type BotMap struct {
	Bots  map[string]*Bot
	Mutex sync.Mutex
}

// bots contains pointers to all the Bot objects in the game, mapped as values with their own names as keys.
var bots BotMap
var numofBots int

type BulletMap struct {
	Bullets map[string]*Bullet
	Mutex   sync.Mutex
}

// bullets contains pointers to all the Bot objects in the game, mapped as values with their own names as keys.
var bullets BulletMap
var numofBullets int

type connectionArray struct {
	Conns []net.Conn
	Mutex sync.Mutex
}

// connections holds all the connections that
// clients have established to the server.
// Used when sending messages to all clients.
var connections connectionArray

// value for defining update frequency to match the tick rate of front end.
var updateFreq int

// setups the map for server use.
func setupMap() {
	setMapConstants()

	mapCenter := Position{X: HALF_MAP_WIDTH, Y: HALF_MAP_HEIGHT}
	mapBoundary := BoundingBox{Center: mapCenter, HalfHeight: HALF_MAP_WIDTH, HalfWidth: HALF_MAP_WIDTH}
	GameMap = QuadTree{Boundary: mapBoundary}

	GameMap.SetChildTrees()
	GameMap.setWallTiles()
}

func setupNewGame() {
	bots.Mutex.Lock()
	bullets.Mutex.Lock()
	connections.Mutex.Lock()

	GameMutex.Lock()
	GameIsRunning = false
	GameMutex.Unlock()

	players = PlayerMap{Players: make(map[string]*Player)}
	bots = BotMap{Bots: make(map[string]*Bot)}
	bullets = BulletMap{Bullets: make(map[string]*Bullet)}

	var connectionsArray [20]net.Conn
	connections = connectionArray{Conns: connectionsArray[:0]}

	fmt.Println("Setting up new game")
}

// spawns stuff
func startNewGame() {
	addBot(200, 80)
	addBot(800, 80)
	addBot(300, 700)
	GameMutex.Lock()
	GameIsRunning = true
	GameMutex.Unlock()
	fmt.Println("New game xD")
}

// main which initiates all functions and loops until crash or quit.
func main() {
	setupMap()
	setPlayerBotConstants()
	updateFreq = 60

	setupNewGame()

	ln, _ := net.Listen("tcp", ":8080")
	fmt.Println("Listening...")

	go continuousUpdate()
	for {
		conn, _ := ln.Accept()
		GameMutex.Lock()
		running := GameIsRunning
		GameMutex.Unlock()
		if running == false {
			connections.Mutex.Lock()
			connections.Conns = append(connections.Conns, conn)
			connections.Mutex.Unlock()
			go handleConn(conn)
		} else {
			conn.Close()
		}
	}
}
