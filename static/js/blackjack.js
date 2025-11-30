let suits = new Array('club', 'diamond', 'heart', 'spade');
let ranks = new Array('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A');

function play(buttonIds) {
    return new Promise(resolve => {
        const handlers = {};

        const allButtons = [
            document.getElementById("hit"),
            document.getElementById("stand"),
            document.getElementById("double-down"),
            document.getElementById("split"),
            document.getElementById("surrender"),
            document.getElementById("insurance"),
            document.getElementById("no-insurance")
        ];

        for (const button of allButtons) {
            if (buttonIds.includes(button.id)) {
                button.disabled = false;
            } else {
                button.disabled = true;
            }
        }

        buttonIds.forEach(id => {
            const btn = document.getElementById(id);
            handlers[id] = () => {
                buttonIds.forEach(otherId => {
                    document.getElementById(otherId)
                        .removeEventListener('click', handlers[otherId]);
                });
                resolve(id);
            };

            btn.addEventListener('click', handlers[id]);
        });
    });
}

class Card {
    constructor(suit, rank) {
        this.suit = suit;
        this.rank = rank;
    }
}

class Deck {
    constructor(number = 1) {
        this.cards = new Array();
        for (let i = 0; i < number; i++) {
            for (let j = 0; j < suits.length; j++) {
                for (let k = 0; k < ranks.length; k++) {
                    this.cards.push(new Card(suits[j], ranks[k]));
                }
            }
        }
    }
    shuffle() {
        let i = this.cards.length, j, temp;
        while (--i > 0) {
            j = Math.floor(Math.random() * (i + 1));
            temp = this.cards[j];
            this.cards[j] = this.cards[i];
            this.cards[i] = temp;
        }
    }
    pop() {
        return this.cards.pop();
    }
    push(card) {
        this.cards.push(card);
    }
}

class Hand {
    constructor(deck, player, stake) {
        this.deck = deck;
        this.player = player;
        this.stake = stake;
        this.cards = new Array();
        this.value = 0;
    }
    get_starting_cards() {
        let card = this.deck.pop();
        let new_val = this.value + this.get_card_value(card);
        this.cards.push(card);
        this.value = new_val;
        card = this.deck.pop();
        new_val = this.value + this.get_card_value(card);
        this.cards.push(card);
        this.value = new_val;
        if (this.value == 21) {
            this.value = 22;
            return this.resolve();
        } else {
            return -1;
        }
    }
    async choose() {
        if (this.cards.length == 2 && this.cards[0].rank == this.cards[1].rank && this.player.hands.length == 1) {
            var choice = await play(["hit", "stand", "double-down", "split", "surrender"]);
        } else if (this.cards.length == 2 && this.player.hands.length == 1) {
            var choice = await play(["hit", "stand", "double-down", "surrender"]);
        } else if (this.cards.length == 2) {
            var choice = await play(["hit", "stand", "double-down"]);
        } else {
            var choice = await play(["hit", "stand"]);
        }

        switch (choice) {
            case "hit":
                return this.hit();
            case "stand":
                return this.stand();
            case "double-down":
                return this.double_down();
            case "split":
                return this.split();
            case "surrender":
                return this.surrender();
        }
    }
    get_card_value(card) {
        for (let i = 0; i < 9; i++) {
            if (card?.rank == ranks[i]) {
                return i + 2;
            }
        }
        for (let i = 9; i < 12; i++) {
            if (card?.rank == ranks[i]) {
                return 10;
            }
        }
        if (card?.rank == ranks[12]) {
            if (this.value < 11) {
                return 11;
            } else {
                return 1;
            }
        }
    }
    resolve() {
        return this.value;
    }
    hit() {
        let card = this.deck.pop();
        let new_val = this.value + this.get_card_value(card);
        this.cards.push(card);
        this.value = new_val;
        if (this.value == 21) {
            return this.resolve();
        } else if (this.value > 21) {
            this.value = 0;
            return this.resolve();
        } else {
            return -1;
        }
    }
    double_down() {
        this.player.chips = this.player.chips - this.stake;
        this.stake = this.stake * 2;
        let card = this.deck.pop();
        let new_val = this.value + this.get_card_value(card);
        this.cards.push(card);
        this.value = new_val;
        if (this.value > 21) {
            this.value = 0;
        }
        return this.resolve();
    }
    stand() {
        return this.resolve();
    }
    split() {
        this.player.chips = this.player.chips + this.stake;
        this.player.split(this);
        return -1;
    }
    surrender() {
        this.player.chips = this.player.chips + Math.floor(this.stake / 2);
        this.stake = Math.ceil(this.stake / 2);
        return this.resolve();
    }
}

class Player {
    constructor(deck, chips, stake) {
        this.hands = new Array(new Hand(deck, this, stake));
        this.chips = chips - stake;
        this.insurance_turn = false;
    }
    split(hand) {
        let hand1 = new Hand(hand.deck, this, hand.stake);
        let hand2 = new Hand(hand.deck, this, hand.stake);
        hand1.value = hand1.get_card_value(hand.cards[0]);
        hand2.value = hand2.get_card_value(hand.cards[1]);
        hand1.cards.push(hand.cards[0]);
        hand2.cards.push(hand.cards[1]);

        let card = hand1.deck.pop();
        let new_val = hand1.value + hand1.get_card_value(card);
        hand1.cards.push(card);
        hand1.value = new_val;

        card = hand2.deck.pop();
        new_val = hand2.value + hand2.get_card_value(card);
        hand2.cards.push(card);
        hand2.value = new_val;

        this.hands[0] = hand1;
        this.hands[1] = hand2;
        console.log(this.hands[0].value);
        for (let k = 0; k < this.hands[0].cards.length; k++) {
            console.log(this.hands[0].cards[k].suit + " " + this.hands[0].cards[k].rank);
        }
        console.log(this.hands[1].value);
        for (let k = 0; k < this.hands[1].cards.length; k++) {
            console.log(this.hands[1].cards[k].suit + " " + this.hands[1].cards[k].rank);
        }
    }
    async insurance_bet() {
        var choice = await play(["insurance", "no-insurance"]);
        if (choice == "insurance") {
            this.chips = this.chips - Math.floor(this.hands[0].stake / 2);
            return Math.floor(this.hands[0].stake / 2);
        } else if (choice == "no-insurance") {
            return 0;
        }
    }
}

class Dealer extends Player {
    constructor(deck, chips, stake) {
        super(deck, chips, stake);
        this.hands = new Array(new DealerHand(deck, this, 0));
    }
}

class DealerHand extends Hand {
    async choose() {
        if (this.value < 17) {
            return this.hit();
        } else {
            return this.stand();
        }
    }
}

class Game {
    constructor(number) {
        this.deck = new Deck();
        this.deck.shuffle();
        this.players = new Array(new Dealer(this.deck, Infinity, 100));
        for (let i = 1; i < number + 1; i++) {
            this.players.push(new Player(this.deck, 10000, 100));
        }
        this.results = new Array();
        for (let i = 0; i < this.players.length; i++) {
            this.results.push(new Array());
        }
    }
    async begin() {
        for (let i = 1; i < this.players.length; i++) {
            console.log(this.players[i].chips);
        }
        for (let i = 0; i < this.players.length; i++) {
            for (let j = 0; j < this.players[i].hands.length; j++) {
                this.results[i][j] = this.players[i].hands[j].get_starting_cards();
                console.log("player " + i + " hand " + j);
                if (i != 0 && j != 1) {
                    for (let k = 0; k < this.players[i].hands[j].cards.length; k++) {
                        console.log(this.players[i].hands[j].cards[k].suit + " " + this.players[i].hands[j].cards[k].rank);
                    }
                } else {
                    for (let k = 0; k < this.players[i].hands[j].cards.length - 1; k++) {
                        console.log(this.players[i].hands[j].cards[k].suit + " " + this.players[i].hands[j].cards[k].rank);
                    }
                }
            }
        }
        if (['10', 'J', 'Q', 'K', 'A'].includes(this.players[0].hands[0].cards[0].rank)) {
            let bets = new Array();
            for (let i = 1; i < this.players.length; i++) {
                bets[i - 1] = await this.players[i].insurance_bet();
            }
            if (this.players[0].hands[0].value == 22) {
                for (let i = 1; i < this.players.length; i++) {
                    this.players[i].chips = this.players[i].chips + bets[i - 1] * 2;
                    bets[i - 1] = 0;
                }
            }
        }
        for (let i = 1; i < this.players.length; i++) {
            for (let j = 0; j < this.players[i].hands.length; j++) {
                while (this.results[i][j] == -1) {
                    this.results[i][j] = await this.players[i].hands[j].choose();
                    if (this.players[i].hands.length > this.results[i].length) {
                        const diff = this.players[i].hands.length - this.results[i].length;
                        for (let k = 0; k < diff; k++) {
                            this.results[i].push(-1);
                        }
                    }
                    console.log("player " + i + " hand " + j);
                    for (let k = 0; k < this.players[i].hands[j].cards.length; k++) {
                        console.log(this.players[i].hands[j].cards[k].suit + " " + this.players[i].hands[j].cards[k].rank);
                    }
                }
            }
        }
        for (let j = 0; j < this.players[0].hands.length; j++) {
            while (this.results[0][j] == -1) {
                this.results[0][j] = await this.players[0].hands[j].choose();
            }
            console.log("player 0 hand " + j);
            for (let k = 0; k < this.players[0].hands[j].cards.length; k++) {
                console.log(this.players[0].hands[j].cards[k].suit + " " + this.players[0].hands[j].cards[k].rank);
            }
        }
        for (let i = 1; i < this.players.length; i++) {
            for (let j = 0; j < this.players[i].hands.length; j++) {
                if (this.players[i].hands[j].value != 0) {
                    if (this.players[i].hands[j].value == this.players[0].hands[0].value) {
                        this.players[i].chips = this.players[i].chips + this.players[i].hands[j].stake;
                        this.players[i].hands[j].stake = 0;
                    } else if (this.players[i].hands[j].value == 22) { 
                        this.players[i].chips = this.players[i].chips + 3 * this.players[i].hands[j].stake;
                        this.players[i].hands[j].stake = 0;
                    } else if (this.players[i].hands[j].value > this.players[0].hands[0].value) {
                        this.players[i].chips = this.players[i].chips + 2 * this.players[i].hands[j].stake;
                        this.players[i].hands[j].stake = 0;
                    }
                }
            }
            console.log(this.players[i].chips);
        }
    }
}

new Game(2).begin();