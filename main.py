import random

blackjack_values = {
    '2S': 2, '3S': 3, '4S': 4, '5S': 5, '6S': 6, '7S': 7, '8S': 8, '9S': 9, '10S': 10,
    'JS': 10, 'QS': 10, 'KS': 10, 'AS': 11,
    '2H': 2, '3H': 3, '4H': 4, '5H': 5, '6H': 6, '7H': 7, '8H': 8, '9H': 9, '10H': 10,
    'JH': 10, 'QH': 10, 'KH': 10, 'AH': 11,
    '2D': 2, '3D': 3, '4D': 4, '5D': 5, '6D': 6, '7D': 7, '8D': 8, '9D': 9, '10D': 10,
    'JD': 10, 'QD': 10, 'KD': 10, 'AD': 11,
    '2C': 2, '3C': 3, '4C': 4, '5C': 5, '6C': 6, '7C': 7, '8C': 8, '9C': 9, '10C': 10,
    'JC': 10, 'QC': 10, 'KC': 10, 'AC': 11
}


def get_random_card():
    card = random.choice(list(blackjack_values.keys()))
    return card, blackjack_values[card]

def opps_play(opps_cards, opps_tot):
    while opps_tot < 17:
        card, value = get_random_card()
        opps_cards.append((card, value))
        opps_tot += value

    return opps_cards, opps_tot


curr_money = 1000

while True:
    print(f"You have {curr_money} in the bank.")

    # Get player bet
    deal = int(input("Place your bet: "))
    if deal > curr_money:
        print("You don't have enough money!")
        break

    curr_money -= deal

    your_cards = [get_random_card(), get_random_card()]
    opps_cards = [get_random_card(), get_random_card()]

    print("\nThese are the cards you got:")
    player_total = sum(value for _, value in your_cards)
    for card, value in your_cards:
        print(f"Your card: {card}, Value: {value}")

    print("\nOpponent's first card:")
    print(f"{opps_cards[0][0]}, Value: {opps_cards[0][1]}")

    opps_total = sum(value for _, value in opps_cards)

    # Player's turn
    while player_total < 21:
        hit_choice = input("Type 'y' to hit or 'n' to stand: ").strip().lower()
        if hit_choice == "y":
            card, value = get_random_card()
            your_cards.append((card, value))
            player_total += value
            print(f"You drew: {card}, Value: {value}")
            print(f"Your total is now: {player_total}")

            if player_total > 21:
                print("Bust! You lose this round.")
                break
        else:
            break

    if player_total <= 21:
        print("\nOpponent's turn...")
        opps_cards, opps_total = opps_play(opps_cards, opps_total)

        # Display opponent's final hand
        print("\nOpponent's final cards:")
        for card, value in opps_cards:
            print(f"{card}, Value: {value}")
        print(f"Opponent's total: {opps_total}")

        if opps_total > 21 or player_total > opps_total:
            print("You win this round!")
            curr_money += deal * 2
        elif player_total == opps_total:
            print("It's a tie! You get your money back.")
            curr_money += deal
        else:
            print("You lose this round!")


    print("\n--- Next Round ---\n")
C:\Users\charmask\PycharmProjects\PythonProject\main.py