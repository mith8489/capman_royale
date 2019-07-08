package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net"
	"time"
)

type CharacterType int

const (
	PlayerChar CharacterType = iota
	BotChar
)

// Request to match JSON
type Request struct {
	Id         int
	Name       string
	Message    string
	X          int
	Y          int
	PlayerName string
	BulletId   string
	Facing     Direction
}

// Response to match JSON
type Response struct {
	Id         int
	Name       string
	Message    string
	X          int
	Y          int
	HitPoints  int
	EntityName string
	BulletId   string
	Facing     string
	Ready      bool
	CharType   CharacterType
}

// Sets entity name of response
func (r *Response) SetEntityName(entityName string) {
	r.EntityName = entityName
}

// Sets x position of response
func (r *Response) SetX(x int) {
	r.X = x
}

// Sets y position of response
func (r *Response) SetY(y int) {
	r.Y = y
}

func (r *Response) SetHitPoints(hp int) {
	r.HitPoints = hp
}

// Sets facing of response
func (r *Response) SetFacing(facing string) {
	r.Facing = facing
}

func (r *Response) SetCharType(charType CharacterType) {
	r.CharType = charType
}

func (r *Response) SetReady(ready bool) {
	r.Ready = ready
}

// setups each connection to the server.
func handleConn(conn net.Conn) {
	decoder := json.NewDecoder(conn)
	for {
		var msg Request
		err := decoder.Decode(&msg)
		if err == io.EOF {
			fmt.Println(err)
			fmt.Println("Connection dropped")
			break
		}
		if err != nil {
			fmt.Println(err)
			return
		}

		handleRequest(msg, conn)
	}
}

// handles each request by their ids with a switch case.
func handleRequest(msg Request, conn net.Conn) {
	var response Response
	var respondToAll bool
	switch msg.Id {

	case 200:
		playerBoundary := BoundingBox{Center: Position{X: msg.X, Y: msg.Y, Facing: East}, HalfHeight: PLAYER_PIXEL_SIZE / 2, HalfWidth: PLAYER_PIXEL_SIZE / 2}
		if _, playerPresent := players.Players[msg.PlayerName]; playerPresent {
			response = Response{Id: 202, Name: "ERR_PLAYER_PRESENT", Message: "Adding failed! Player name already exists."}
			respondToAll = false
			fmt.Println("Player addition failed! Player already exists.")
		} else if GameMap.IsObjectOnWall(playerBoundary) {
			response = Response{Id: 203, Name: "ERR_WALL_CLASH", Message: "Adding failed! Tried to place player on wall.", X: msg.X, Y: msg.Y}
			respondToAll = false
			fmt.Println("Player addition failed! Tried to place player on wall.")
		} else {
			addPlayer(msg.PlayerName, playerBoundary)
			response = Response{Id: 201, Name: "ADDED_CHARACTER", EntityName: msg.PlayerName, Message: "Success! Player added: " + msg.PlayerName, X: msg.X, Y: msg.Y, HitPoints: PLAYER_HIT_POINTS, Facing: msg.Facing.String(), CharType: PlayerChar, Ready: false}
			respondToAll = true
		}

	case 300:
		if player, isPresent := players.Players[msg.PlayerName]; isPresent {
			player.InputChan <- "KILL"
		} else {
			response = Response{Id: 302, Name: "ERR_PLAYER_NOT_FOUND", Message: "Removal failed! Player does not exist."}
			respondToAll = false
			fmt.Println("Player removal failed! Player does not exist.")
		}

	case 400:
		players.Mutex.Lock()
		if _, playerPresent := players.Players[msg.PlayerName]; playerPresent {
			players.Mutex.Unlock()
			player := players.Players[msg.PlayerName]
			player.moveEntity(msg.X, msg.Y)
		} else {
			players.Mutex.Unlock()
		}
	case 500:
		if player, isPresent := players.Players[msg.PlayerName]; isPresent {
			player.FireBullet()
		}

	case 800:
		players.Mutex.Lock()
		if player, isPresent := players.Players[msg.PlayerName]; isPresent {
			player.Mutex.Lock()
			player.Ready = true
			response = Response{Id: 801, Name: "PLAYER_IS_READY", Message: "PLAYER IS READY", EntityName: player.Name}
			fmt.Println(player.Name + " is ready")
			player.Mutex.Unlock()
			writeJsonMessage(response, nil, true)
		}
		players.Mutex.Unlock()

		if isAllPlayersReady() {
			response = Response{Id: 802, Name: "ALL_PLAYERS_ARE_READY", Message: "All players are ready"}
			writeJsonMessage(response, nil, true)
			fmt.Println("All players ready, starting game")
			startNewGame()
		}

	case 900:
		sendInitState(conn)

	case 1000:
		sendAllPlayers()
	}
	if response.Id != 0 && msg.Id != 800 && msg.Id != 900 && msg.Id != 1000 {
		writeJsonMessage(response, conn, respondToAll)
	}
}

// writes a json message to suitable connections
func writeJsonMessage(response Response, conn net.Conn, toAll bool) {
	connections.Mutex.Lock()
	b, err := json.Marshal(response)
	if err != nil {
		panic(err)
	}
	if toAll {
		for i := range connections.Conns {
			connections.Conns[i].Write(b)
		}
	} else {
		conn.Write(b)
	}
	connections.Mutex.Unlock()
}

func (entity *Entity) setUpdateMessage(message Response) Response {
	entity.Mutex.Lock()
	defer entity.Mutex.Unlock()
	message.SetEntityName(entity.Name)
	message.SetX(entity.Boundary.Center.X)
	message.SetY(entity.Boundary.Center.Y)
	message.SetHitPoints(entity.HitPoints)
	message.SetFacing(entity.Boundary.Center.Facing.String())
	return message
}

func sendAllPlayers() {
	message := Response{Id: 201, Name: "ADDED_CHARACTER"}
	for i := range players.Players {
		plr := players.Players[i]
		message.SetEntityName(plr.Name)
		message.SetReady(plr.Ready)
		writeJsonMessage(message, nil, true)
	}
}

func sendInitState(conn net.Conn) {
	message := Response{Id: 201, Name: "ADDED_CHARACTER"}
	message.SetCharType(PlayerChar)
	for i := range players.Players {
		plr := players.Players[i]
		message = plr.setUpdateMessage(message)
		writeJsonMessage(message, conn, false)
	}

	message.SetCharType(BotChar)
	for i := range bots.Bots {
		bot := bots.Bots[i]
		message = bot.setUpdateMessage(message)
		fmt.Println("BOT HP:", message.HitPoints)
		writeJsonMessage(message, conn, false)
	}
}

// writes a json message containing all info from players, bots and bullets.
func updateState() {
	message := Response{Id: 101, Name: "STATE_UPDATE"}
	players.Mutex.Lock()
	for i := range players.Players {
		plr := players.Players[i]
		message = plr.setUpdateMessage(message)
		writeJsonMessage(message, nil, true)
	}
	players.Mutex.Unlock()
	bots.Mutex.Lock()
	message.SetCharType(BotChar)
	for i := range bots.Bots {
		bot := bots.Bots[i]
		message = bot.setUpdateMessage(message)
		writeJsonMessage(message, nil, true)
	}
	bots.Mutex.Unlock()
	message = Response{Id: 102, Name: "BULLET_UPDATE"}
	bullets.Mutex.Lock()
	for i := range bullets.Bullets {
		bullet := bullets.Bullets[i]
		bullet.Mutex.Lock()
		message.SetEntityName(bullet.Id)
		message.SetX(bullet.Boundary.Center.X)
		message.SetY(bullet.Boundary.Center.Y)
		message.SetFacing(bullet.Boundary.Center.Facing.String())
		bullet.Mutex.Unlock()
		writeJsonMessage(message, nil, true)
	}
	bullets.Mutex.Unlock()
}

// updates the states depending on the updateFreq. Set to 1 sec/updateFreq.
func continuousUpdate() {
	for {
		timeWait := (1000000000 * time.Nanosecond) / time.Duration(updateFreq)
		updateState()
		time.Sleep(timeWait)
	}
}
