"""Vendored from Shaurya-S0603/PokerBots (ashwing_sdk) @ dc87080d1030ebf6df900eab2d8938acaf830878, patched for the offline arena (see PROVENANCE.md)."""

ranks = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
suits = ["♣️","♦️","♠️","♥️"]

def cards_on_table(table, hand):
  cards = hand + table
  return cards

def rules(cards):
  highcard = max(cards, key=lambda x: ranks.index(x[0]))
  pair = False
  pair_card = []
  twopair = False
  twopair_card = []
  threeofakind = False
  threeofakind_card = []
  fourofakind = False
  fourofakind_card = []
  straight = False
  straight_cards = []
  flush = False
  flush_cards = []
  fullhouse = False
  fullhouse_cards = []
  straightflush = False
  straightflush_cards = []
  royalflush = False
  royalflush_cards = []

  royalflush_compare_cards = []
  straightflush_compare_cards = []
  fourofakind_compare_card = []
  fullhouse_compare_cards = []
  flush_compare_cards = []
  straight_compare_cards = []
  threeofakind_compare_card = []
  twopair_compare_card = []
  pair_compare_card = []
  highcard_compare = []

  frequency = {"A":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"J":0,"Q":0,"K":0}
  for card in cards:
    frequency[card[0]] += 1

  for key in frequency:
    if frequency[key] == 2:
      pair = True
      pair_card.append(key)
    if frequency[key] == 3:
      threeofakind = True
      threeofakind_card.append(key)
    if frequency[key] == 4:
      fourofakind = True
      fourofakind_card.append(key)

  if (threeofakind and pair) or (len(threeofakind_card) == 2) or (fourofakind and threeofakind) or (fourofakind and pair):
    fullhouse = True
    cards_full = [max([card for card in frequency if frequency[card] >= 3], key=lambda x: ranks.index(x)), max(pair_card, key=lambda x: ranks.index(x)) if pair_card else max([card for card in frequency if frequency[card] >= 2 and card != max([c for c in frequency if frequency[c] >= 3], key=lambda x: ranks.index(x))], key=lambda x: ranks.index(x))]
    fullhouse_cards.extend(cards_full)

  if len(pair_card) >= 2:
    twopair = True
    twopair_card.extend(sorted(pair_card, key=lambda x: ranks.index(x), reverse = True)[0:2])

  for card in cards:
    if card[0] not in straight_cards:
      straight_cards.append(card[0])

  straight_cards.sort(key=lambda x: ranks.index(x))

  AceLow = straight_cards.copy()

  while len(straight_cards)>=5:
    for i in range(len(straight_cards)-1,len(straight_cards)-5,-1):
      if ranks.index(straight_cards[i]) == ranks.index(straight_cards[i-1])+1:
        straight = True
      else:
        straight = False
        break
    if straight:
      break
    else:
      straight_cards.pop(-1)

  if straight and len(straight_cards) >= 5:
    straight_cards = straight_cards[-5:]

  if not straight:
    reqd = ["A","2","3","4","5"]
    if all(card in AceLow for card in reqd):
      straight = True
      straight_cards = ["A","2","3","4","5"]
    else:
      straight = False
      straight_cards = []

  frequency_suits = {"♣️":0,"♦️":0,"♠️":0,"♥️":0}
  for card in cards:
    frequency_suits[card[1]] += 1

  if frequency_suits["♣️"] >= 5 or frequency_suits["♦️"] >= 5 or frequency_suits["♠️"] >= 5 or frequency_suits["♥️"] >= 5:
    flush = True
    straightflush_cards.extend([card[0] for card in cards if card[1] in [suit for suit in frequency_suits if frequency_suits[suit] >= 5]])
    flush_cards.extend(sorted([card for card in cards if card[1] in [suit for suit in frequency_suits if frequency_suits[suit] >= 5]], key=lambda x: ranks.index(x[0]), reverse = True)[:5])

  straightflush_cards.sort(key=lambda x: ranks.index(x))
  AceLowFlush = straightflush_cards.copy()
  while len(straightflush_cards)>=5:
    for i in range(len(straightflush_cards)-1,len(straightflush_cards)-5,-1):
      if ranks.index(straightflush_cards[i]) == ranks.index(straightflush_cards[i-1])+1:
        straightflush = True
      else:
        straightflush = False
        break
    if straightflush:
      break
    else:
      straightflush_cards.pop(-1)

  if straightflush and len(straightflush_cards) >= 5:
    straightflush_cards = straightflush_cards[-5:]

  if not straightflush:
    reqd = ["A","2","3","4","5"]
    if all(card in AceLowFlush for card in reqd):
      straightflush = True
      straightflush_cards = ["A","2","3","4","5"]
    else:
      straightflush = False
      straightflush_cards = []

  if straightflush:
    reqd = ["A","K","Q","J","10"]
    if all(card in straightflush_cards for card in reqd):
      royalflush = True
      royalflush_cards.extend(straightflush_cards)

  highcard_compare = [card[0] for card in sorted(cards, key=lambda x: ranks.index(x[0]), reverse=True)[:5]]
  if pair:
    pair_compare_card = [max([card for card in frequency if frequency[card] == 2], key=lambda x: ranks.index(x))] + sorted([card for card in frequency if frequency[card]>0 and card != max([card for card in frequency if frequency[card] == 2], key=lambda x: ranks.index(x))], key=lambda x: ranks.index(x), reverse = True)[:3]

  if twopair:
    twopair_compare_card = sorted(twopair_card, key=lambda x: ranks.index(x), reverse = True)[:2]+[max([card for card in frequency if frequency[card] > 0 and card not in twopair_card], key=lambda x: ranks.index(x))]

  if threeofakind:
    threeofakind_compare_card = [max([card for card in frequency if frequency[card] == 3], key=lambda x: ranks.index(x))] + sorted([card for card in frequency if frequency[card]>0 and card != max([card for card in frequency if frequency[card] == 3], key=lambda x: ranks.index(x))], key=lambda x: ranks.index(x), reverse = True)[:2]

  if fourofakind:
    fourofakind_compare_card = [max([card for card in frequency if frequency[card] == 4], key=lambda x: ranks.index(x))] + sorted([card for card in frequency if frequency[card]>0 and card != max([card for card in frequency if frequency[card] == 4], key=lambda x: ranks.index(x))], key=lambda x: ranks.index(x), reverse = True)[:1]

  if fullhouse:
    fullhouse_compare_cards = fullhouse_cards.copy()

  if straight:
    straight_compare_cards = [straight_cards[-1]]

  if straightflush:
    straightflush_compare_cards = [straightflush_cards[-1]]

  if flush:
    flush_compare_cards = [card[0] for card in flush_cards]

  if royalflush:
    royalflush_compare_cards = [royalflush_cards[-1]]

  detected = {"Royal Flush": royalflush, "Straight Flush": straightflush, "4 of a kind": fourofakind, "Full House": fullhouse, "Flush": flush, "Straight": straight, "3 of a kind": threeofakind, "2 Pair": twopair, "Pair": pair, "High Card": True}
  detected_cards = {"Royal Flush": royalflush_compare_cards, "Straight Flush": straightflush_compare_cards, "4 of a kind": fourofakind_compare_card, "Full House": fullhouse_compare_cards, "Flush": flush_compare_cards, "Straight": straight_compare_cards, "3 of a kind": threeofakind_compare_card, "2 Pair": twopair_compare_card, "Pair": pair_compare_card, "High Card": highcard_compare}
  return [detected, detected_cards]

def highest_hand(cards):
  win_ranks = {"High Card": 1, "Pair": 2, "2 Pair": 3, "3 of a kind": 4, "Straight": 5, "Flush": 6, "Full House": 7, "4 of a kind": 8, "Straight Flush": 9, "Royal Flush": 10}
  detected, detected_cards = rules(cards)
  valid = []
  for i in detected.keys():
    if detected[i]:
      valid.append(i)

  return max(valid, key=lambda x: win_ranks[x]), detected_cards[max(valid, key=lambda x: win_ranks[x])]
