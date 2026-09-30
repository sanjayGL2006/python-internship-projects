import random
import time

# =========================================================
#                 THE HAUNTED HOTEL
# =========================================================

def slow(text, speed=0.02):
    for c in text:
        print(c, end="", flush=True)
        time.sleep(speed)
    print()


def line():
    print("=" * 60)


def game_over():
    print("\n")
    line()
    print("                 💀 GAME OVER 💀")
    line()
    print("The hotel has claimed you...")
    print("\nThanks for playing!")
    exit()


def win():
    print("\n")
    line()
    print("              🎉 YOU ESCAPED! 🎉")
    line()
    print("You run outside the hotel as the sun rises.")
    print("Behind you, every window suddenly goes dark.")
    print("\n🏆 YOU SURVIVED THE HAUNTED HOTEL!")
    exit()


# ---------------- PLAYER ----------------

player = {
    "health": 100,
    "sanity": 100,
    "keys": 0,
    "coins": 0,
    "flashlight": True
}


# ---------------- INTRO ----------------

print("\n")
line()
print("             👻 THE HAUNTED HOTEL 👻")
line()

slow("\nYou wake up inside an abandoned hotel.")
slow("The front door is locked.")
slow("The lights are flickering.")
slow("Something is walking upstairs...")

name = input("\nWhat is your name? ")

slow(f"\nWelcome, {name}...")
slow("You hear a voice whisper:")
slow('"Find the three keys... or stay here forever."')

input("\nPress ENTER to continue...")


# ---------------- GAME LOOP ----------------

rooms = [
    "Reception",
    "Kitchen",
    "Library",
    "Basement",
    "Second Floor",
    "Attic"
]

current_room = 0

while True:

    print("\n")
    line()
    print("📍 LOCATION:", rooms[current_room])
    print(
        f"❤️ Health: {player['health']}   "
        f"🧠 Sanity: {player['sanity']}   "
        f"🔑 Keys: {player['keys']}/3   "
        f"🪙 Coins: {player['coins']}"
    )
    line()

    print("""
1. Explore
2. Check inventory
3. Rest
4. Move to another room
5. Quit
""")

    choice = input("Choose: ")

    # ---------------- EXPLORE ----------------

    if choice == "1":

        event = random.randint(1, 8)

        if event == 1:
            print("\n👻 A GHOST APPEARS!")

            if random.random() < 0.5:
                print("The ghost attacks you!")
                damage = random.randint(10, 25)
                player["health"] -= damage
                print(f"You lose {damage} health.")
            else:
                print("The ghost disappears...")
                print("You feel lucky.")

        elif event == 2:
            print("\n🔑 YOU FOUND A KEY!")
            player["keys"] += 1

            if player["keys"] >= 3:
                print("You now have all three keys!")

        elif event == 3:
            print("\n🪙 You found some coins!")
            coins = random.randint(5, 20)
            player["coins"] += coins
            print(f"You found {coins} coins.")

        elif event == 4:
            print("\n🩹 You found a medical kit.")
            heal = random.randint(15, 30)
            player["health"] = min(100, player["health"] + heal)
            print(f"You recovered {heal} health.")

        elif event == 5:
            print("\n😱 You hear footsteps behind you.")

            if random.random() < 0.7:
                print("You turn around...")
                print("Nothing is there.")

                player["sanity"] -= 10
                print("Your sanity decreases.")
            else:
                print("A shadow grabs you!")
                player["health"] -= 20

        elif event == 6:
            print("\n📖 You found an old diary.")
            print("""
The diary says:

"Three keys open the front door.
But the hotel changes every midnight."

You suddenly hear a clock ticking...
""")

        elif event == 7:
            print("\n🕯️ You found a strange candle.")
            print("The flame turns BLUE.")

            player["sanity"] += 10
            player["sanity"] = min(100, player["sanity"])

        else:
            print("\n...")
            print("Nothing happens.")
            print("But you feel like someone is watching you.")

        # Random sanity event
        if random.random() < 0.2:
            player["sanity"] -= 5
            print("\n🧠 Your sanity decreases...")

    # ---------------- INVENTORY ----------------

    elif choice == "2":

        print("\n🎒 INVENTORY")
        print("-" * 30)

        print("🔑 Keys:", player["keys"])
        print("🪙 Coins:", player["coins"])
        print("🔦 Flashlight:", "Yes" if player["flashlight"] else "No")

    # ---------------- REST ----------------

    elif choice == "3":

        print("\nYou sit down for a moment...")

        time.sleep(1)

        if random.random() < 0.3:
            print("\n😈 BAD IDEA!")

            damage = random.randint(5, 15)
            player["health"] -= damage

            print("Something attacks you while you rest!")

        else:
            player["health"] += 10
            player["sanity"] += 10

            player["health"] = min(100, player["health"])
            player["sanity"] = min(100, player["sanity"])

            print("You feel slightly better.")

    # ---------------- MOVE ----------------

    elif choice == "4":

        print("\nWhere do you want to go?")

        for i, room in enumerate(rooms):
            print(f"{i + 1}. {room}")

        try:
            destination = int(input("\nChoose room: "))

            if 1 <= destination <= len(rooms):

                current_room = destination - 1

                print(f"\n🚪 You enter the {rooms[current_room]}.")

                # Special rooms

                if rooms[current_room] == "Basement":
                    print("\nThe basement is extremely dark.")

                    if random.random() < 0.5:
                        print("👹 SOMETHING ATTACKS YOU!")

                        damage = random.randint(15, 30)
                        player["health"] -= damage

                elif rooms[current_room] == "Attic":
                    print("\nYou climb into the attic.")

                    print("You see an old mirror.")

                    print("The mirror shows YOU...")

                    time.sleep(2)

                    print("But your reflection is smiling.")

                    player["sanity"] -= 20

                elif rooms[current_room] == "Library":
                    print("\n📚 Thousands of books surround you.")

                    if random.random() < 0.5:
                        print("You discover a hidden passage!")
                        player["sanity"] += 10

            else:
                print("Invalid room.")

        except ValueError:
            print("Please enter a number.")

    # ---------------- QUIT ----------------

    elif choice == "5":

        print("\nYou leave the game...")
        print("The hotel whispers:")
        print('"Come back..."')
        break

    else:
        print("\n❌ Invalid choice.")

    # ---------------- DEATH CHECK ----------------

    if player["health"] <= 0:
        game_over()

    if player["sanity"] <= 0:
        print("\n🧠 You have completely lost your sanity...")
        game_over()

    # ---------------- WIN CHECK ----------------

    if player["keys"] >= 3:

        print("\n🔑 You have collected all three keys!")

        answer = input(
            "Do you want to try opening the front door? (yes/no): "
        ).lower()

        if answer == "yes":

            print("\nYou insert the keys...")

            time.sleep(1)

            print("🔑")
            print("🔑")
            print("🔑")

            time.sleep(1)

            if random.random() < 0.75:
                win()
            else:
                print("\n😱 THE DOOR DOESN'T OPEN!")

                print("Something is holding it from the other side.")

                player["sanity"] -= 25


print("\nGame closed.")
