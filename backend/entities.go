package main

import (
	"fmt"
	"math/rand"
	"strconv"
	"sync"
	"time"
)

// Our direction type ordered from 0-7 each representing a point of a compass
type Direction int

const (
	North Direction = iota
	NorthEast
	East
	SouthEast
	South
	SouthWest
	West
	NorthWest
	None
)

// Maps the directions to an int
func (d Direction) String() string {
	return [...]string{"North", "NorthEast", "East", "SouthEast", "South", "SouthWest", "West", "NorthWest"}[d]
}

// Translates a string to a direction
func getDirection(dirStr string) Direction {
	if dirStr == "North" {
		return North
	}

	if dirStr == "NorthEast" {
		return NorthEast
	}

	if dirStr == "SouthEast" {
		return SouthEast
	}

	if dirStr == "SouthWest" {
		return SouthWest
	}

	if dirStr == "NorthWest" {
		return NorthWest
	}
	if dirStr == "East" {
		return East
	}
	if dirStr == "South" {
		return South
	}
	if dirStr == "West" {
		return West
	}
	return None
}

type Entity struct {
	Name       string
	Boundary   BoundingBox
	MvmtSpeed  int
	HitPoints  int
	Invincible bool
	InputChan  chan string
	Mutex      sync.Mutex
}

func (entity *Entity) moveEntity(moveX int, moveY int) {
	entity.Mutex.Lock()
	entity.setFacing(moveX, moveY)

	testXY := entity.Boundary
	testY := entity.Boundary
	testX := entity.Boundary

	testXY.Center.X += moveX * entity.MvmtSpeed
	testXY.Center.Y += moveY * entity.MvmtSpeed

	testX.Center.X += moveX * entity.MvmtSpeed
	testY.Center.Y += moveY * entity.MvmtSpeed

	if !GameMap.IsObjectOnWall(testXY) {
		entity.Boundary = testXY
	} else if moveX != 0 && !GameMap.IsObjectOnWall(testX) {
		entity.Boundary = testX
	} else if moveY != 0 && !GameMap.IsObjectOnWall(testY) {
		entity.Boundary = testY
	}
	entity.Mutex.Unlock()
}

func (entity *Entity) setFacing(moveX int, moveY int) {
	if moveY < 0 && moveX < 0 {
		entity.Boundary.Center.Facing = NorthWest
	} else if moveY < 0 && moveX > 0 {
		entity.Boundary.Center.Facing = NorthEast
	} else if moveY > 0 && moveX < 0 {
		entity.Boundary.Center.Facing = SouthWest
	} else if moveY > 0 && moveX > 0 {
		entity.Boundary.Center.Facing = SouthEast
	} else if moveY < 0 {
		entity.Boundary.Center.Facing = North
	} else if moveY > 0 {
		entity.Boundary.Center.Facing = South
	} else if moveX < 0 {
		entity.Boundary.Center.Facing = West
	} else if moveX > 0 {
		entity.Boundary.Center.Facing = East
	}
}

func (entity *Entity) getXFacing() int {
	xFacing := 0
	facing := entity.Boundary.Center.Facing
	if facing < 4 && facing > 0 {
		xFacing = 1
	} else if facing < 8 && facing > 4 {
		xFacing = -1
	}
	return xFacing
}

func (entity *Entity) getYFacing() int {
	yFacing := 0
	facing := entity.Boundary.Center.Facing
	if facing < 2 || facing > 6 {
		yFacing = -1
	} else if facing > 8 || (facing < 6 && facing > 2) {
		yFacing = 1
	}
	return yFacing
}

func (entity *Entity) isAlive() bool {
	return entity.HitPoints > 0
}

func (entity *Entity) takeDamage(damage int, invincTime time.Duration) {
	entity.HitPoints -= damage
	fmt.Println("Entity has hp: ", entity.HitPoints)
	go entity.makeInvincible(invincTime)
}

func (entity *Entity) makeInvincible(invincTime time.Duration) {
	entity.Mutex.Lock()
	entity.Invincible = true
	entity.Mutex.Unlock()

	time.Sleep(invincTime)

	entity.Mutex.Lock()
	entity.Invincible = false
	entity.Mutex.Unlock()
}

// Player contains all the information relating to players
// and their avatars.
type Player struct {
	Entity
	Wpn   Weapon
	Ready bool
}

type Weapon struct {
	CoolDown int
	Ammo     int
}

type Bot struct {
	Entity
	Type        string
	AttackPower int
}

type Bullet struct {
	Id        string
	Boundary  BoundingBox
	FiredBy   *Player
	MvmtSpeed int
	MoveX     int //-1, 0, or 1
	MoveY     int //-1, 0 or 1
	Damage    int
	IsMoving  bool
	Mutex     sync.Mutex
	InputChan chan string
}

// addPlayer creates a new Player object and maps
// a pointer to it to its own name in the players map.
func addPlayer(name string, playerBoundary BoundingBox) {
	plr := Player{Entity: Entity{Name: name, Boundary: playerBoundary, MvmtSpeed: PLAYER_MVMT_SPEED, HitPoints: PLAYER_HIT_POINTS, InputChan: make(chan string)}, Wpn: Weapon{CoolDown: 0}, Ready: false}
	players.Mutex.Lock()
	players.Players[name] = &plr
	players.Mutex.Unlock()
	fmt.Println("Added player:", plr.Name)
	fmt.Println("Facing:", plr.Boundary.Center.Facing)
	go plr.runPlayer()
}

// addBot creates a new Bot object and maps a pointer to it to its own name in the bots map
func addBot(xPos int, yPos int) {
	pos := Position{X: xPos, Y: yPos, Facing: East}
	if !GameMap.GetTileOfPoint(pos).IsWall {
		boundary := BoundingBox{Center: pos, HalfHeight: BOT_PIXEL_SIZE / 2, HalfWidth: BOT_PIXEL_SIZE / 2}
		bot := Bot{Entity: Entity{Name: "Bot" + strconv.Itoa(numofBots), Boundary: boundary, MvmtSpeed: BOT_MVMT_SPEED, HitPoints: BOT_HIT_POINTS, InputChan: make(chan string)}, AttackPower: BOT_ATTACK_POWER}
		numofBots++
		bots.Bots[bot.Name] = &bot
		addBotMsg := Response{Id: 201, Name: "ADDED_CHARACTER", EntityName: bot.Name, Message: "Added new bot to game", X: xPos, Y: yPos, HitPoints: bot.HitPoints, Facing: pos.Facing.String(), CharType: BotChar}
		fmt.Println("Bot hp:", addBotMsg.HitPoints)
		writeJsonMessage(addBotMsg, nil, true)
		go bot.runBot()
	} else {
		fmt.Println("Bot addition failed. Tried to place bot on wall.")
	}
}

func (player *Player) checkBotCollision(timeWait time.Duration) {
	invincTime := (1000000000 * time.Nanosecond)
	bots.Mutex.Lock()
	for _, bot := range bots.Bots {
		player.Mutex.Lock()
		bot.Mutex.Lock()
		if player.Boundary.intersectsBox(bot.Boundary) && !player.Invincible {
			player.takeDamage(bot.AttackPower, invincTime)
			bot.Mutex.Unlock()
			player.Mutex.Unlock()
			fmt.Println("Player took damage")
		} else {
			bot.Mutex.Unlock()
			player.Mutex.Unlock()
		}
	}
	bots.Mutex.Unlock()
}

func (entity *Entity) checkBulletCollision() {
	invincTime := (1000000000 * time.Nanosecond)
	entity.Mutex.Lock()
	bullets.Mutex.Lock()
	for _, bullet := range bullets.Bullets {

		bullet.Mutex.Lock()
		if entity.Boundary.intersectsBox(bullet.Boundary) {
			if !(bullet.FiredBy.Name == entity.Name) {
				if !entity.Invincible {
					entity.takeDamage(bullet.Damage, invincTime)
				}
				bullet.IsMoving = false
			}
		}
		bullet.Mutex.Unlock()
	}
	bullets.Mutex.Unlock()
	entity.Mutex.Unlock()
}

func (player *Player) runPlayer() {
	timeWait := (1000000000 * time.Nanosecond) / time.Duration(updateFreq)
	for player.isAlive() {
		select {
		case msg := <-player.InputChan:
			if msg == "KILL" {
				fmt.Println("PLAYER REMOVED BY DISCONNECTION")
				player.Mutex.Lock()
				player.HitPoints = 0
				player.Mutex.Unlock()
			}
		case <-time.After(timeWait):
			player.checkBulletCollision()
			player.checkBotCollision(timeWait)
		}
	}
	killPlayer(player.Name)
	checkWinningPlayer()
}

func (bot *Bot) runBot() {
	turnTime := 60
	turnCounter := 0
	xDirs := []int{-1, 0, 1, 0}
	yDirs := []int{-1, 0, 1, 0}
	xIndex := 2
	yIndex := 1
	timeWait := (1000000000 * time.Nanosecond) / time.Duration(updateFreq)
	for bot.isAlive() {
		select {
		case msg := <-bot.InputChan:
			if msg == "KILL" {
				fmt.Println("BOT REMOVED")
				bot.Mutex.Lock()
				bot.HitPoints = 0
				bot.Mutex.Unlock()
			}
		case <-time.After(timeWait):
			if turnCounter >= turnTime {
				xIndex = rand.Intn(4)
				yIndex = rand.Intn(4)
				turnCounter = rand.Intn(turnTime)
			}
			bot.moveEntity(xDirs[xIndex], yDirs[yIndex])
			turnCounter++
			bot.checkBulletCollision()
		}
	}
	killBot(bot.Name)
	checkWinningPlayer()
}

// killPlayer removes a player by name from the players map.
func killPlayer(name string) {
	players.Mutex.Lock()
	delete(players.Players, name)
	players.Mutex.Unlock()
	killMsg := Response{Id: 301, Name: "KILLED_ENTITY", EntityName: name, Message: "Entity killed: " + name, CharType: PlayerChar}
	fmt.Println("Killed player:", name)
	writeJsonMessage(killMsg, nil, true)
}

func killBot(name string) {
	bots.Mutex.Lock()
	delete(bots.Bots, name)
	bots.Mutex.Unlock()
	killMsg := Response{Id: 301, Name: "KILLED_ENTITY", EntityName: name, Message: "Entity killed: " + name, CharType: BotChar}
	fmt.Println("Removed bot:", name)
	writeJsonMessage(killMsg, nil, true)
	fmt.Println("BOT KILLED")
}

func (player *Player) FireBullet() {
	player.Mutex.Lock()
	if player.Wpn.CoolDown == 0 {
		bulletBoundary := BoundingBox{

			Center:     Position{X: player.Boundary.Center.X, Y: player.Boundary.Center.Y},
			HalfHeight: BULLET_PIXEL_SIZE / 2,
			HalfWidth:  BULLET_PIXEL_SIZE / 2}

		numofBullets += 1
		bullet := Bullet{Id: "Bullet" + strconv.Itoa(numofBullets), Boundary: bulletBoundary, FiredBy: player, MoveX: player.getXFacing(), MoveY: player.getYFacing(), MvmtSpeed: BULLET_MVMT_SPEED, Damage: BULLET_DMG, IsMoving: true, InputChan: make(chan string)}
		bullets.Mutex.Lock()
		bullets.Bullets[bullet.Id] = &bullet
		bullets.Mutex.Unlock()
		firedMsg := Response{Id: 501, Name: "FIRED_BULLET", EntityName: bullet.Id, X: bullet.Boundary.Center.X, Y: bullet.Boundary.Center.Y, Message: "Fired bullet: " + bullet.Id}
		writeJsonMessage(firedMsg, nil, true)
		go bullet.MoveBullet()
		player.Wpn.CoolDown = 300000000
		player.Mutex.Unlock()
		go player.CoolDownWpn()
	} else {
		player.Mutex.Unlock()
	}
}

func (player *Player) CoolDownWpn() {
	timeWait := time.Nanosecond * time.Duration(player.Wpn.CoolDown)
	time.Sleep(timeWait)
	player.Mutex.Lock()
	player.Wpn.CoolDown = 0
	player.Mutex.Unlock()
}

func (bullet *Bullet) MoveBullet() {
	timeWait := (1000000000 * time.Nanosecond) / time.Duration(updateFreq)
	moving := true
	for moving {
		bullet.Mutex.Lock()
		moving = bullet.IsMoving
		if !GameMap.IsObjectOnWall(bullet.Boundary) {
			bullet.Boundary.Center.X += bullet.MoveX * bullet.MvmtSpeed
			bullet.Boundary.Center.Y += bullet.MoveY * bullet.MvmtSpeed
		} else {
			moving = false
		}
		bullet.Mutex.Unlock()
		time.Sleep(timeWait)
	}

	deleteBullet(bullet.Id)
}

func deleteBullet(id string) {
	bullets.Mutex.Lock()
	delete(bullets.Bullets, id)
	bullets.Mutex.Unlock()
	deleteMsg := Response{Id: 601, Name: "REMOVED_BULLET", EntityName: id, Message: "Removed bullet: " + id}
	writeJsonMessage(deleteMsg, nil, true)
}

// winningPlayer sends a message when there is only one player left. Deletes the player left after sending the player to a VictoryScene
func checkWinningPlayer() {
	players.Mutex.Lock()
	if (len(bots.Bots) == 0) && (len(players.Players) == 1) {
		for i := range players.Players { //kanske onödig for loop då det bara är en spelare i mapen
			plr := players.Players[i]
			plr.Mutex.Lock()
			name := plr.Name
			plr.Mutex.Unlock()
			winMsg := Response{Id: 701, Name: "WINNING_PLAYER", EntityName: name, Message: "Player won: " + name}
			writeJsonMessage(winMsg, nil, true)
			delete(players.Players, name)
			fmt.Println("Removed player:", name)
			endGame()
		}
	} else if len(players.Players) == 0 {
		for i := range bots.Bots {
			bots.Bots[i].InputChan <- "KILL"
		}
		endGame()
	} else {
		players.Mutex.Unlock()
	}
}

func endGame() {
	kickResponse := Response{Id: 1101, Name: "CLOSE_CONNECTION"}
	writeJsonMessage(kickResponse, nil, true)
	setupNewGame()
}

//checks if all players are ready
func isAllPlayersReady() bool {
	players.Mutex.Lock()
	for i := range players.Players { //kanske onödig for loop då det bara är en spelare i mapen
		plr := players.Players[i]
		plr.Mutex.Lock()
		isPlayerReady := plr.Ready
		plr.Mutex.Unlock()

		if isPlayerReady == false {
			players.Mutex.Unlock()
			return false
		}
	}
	players.Mutex.Unlock()
	return true
}
