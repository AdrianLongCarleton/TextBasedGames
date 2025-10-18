# TextBasedGames

## Battleship
So far this project has the backend implemented. Most of the complexity that went into this has to do with the requirement that both application must be able to quit at any time. Python has no way for it's IO to be interupted.

Input in the battleship game, works by looping until one of two condition become true: either the user finsishes typing their input, or the input is interupted by a quit request from the other player. To efficiently achieve this goal the input for the player1 making their move is run in parralel. Before the begining of the afformentioned loop a flag is set that allows another thread to process player1's input in the terminal. When player1 enters a character return, the flag is set to false and the loop detects a break condition. Alternativly if the loop detects that player2 has sent a quit request then the input thread is interupted an execution continues.
