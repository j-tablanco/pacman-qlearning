for VARIABLE in 1 2 3 4 5 6 7 8 9 10
do
	echo "ronda numero $VARIABLE"
	echo "mapa 1"
	timeout 5m python busters.py -p QLearningAgent -l laberynths/labAA1 -k 1 -g RandomGhost 
	echo "mapa 2"
	timeout 5m python busters.py -p QLearningAgent -l laberynths/labAA2 -k 2 -g RandomGhost
	echo "mapa 4"
	timeout 5m python busters.py -p QLearningAgent -l laberynths/labAA4 -k 3 -g RandomGhost
	echo "mapa 5"
	timeout 5m python busters.py -p QLearningAgent -l laberynths/labAA5 -k 3 -g RandomGhost
	echo "mapa 3"
	timeout 5m python busters.py -p QLearningAgent -l laberynths/labAA3 -k 3 -g RandomGhost
done
