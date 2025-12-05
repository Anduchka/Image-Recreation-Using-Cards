from PIL import Image
import random
import numpy as np

from CardDeck import cards

CARD_STANDART_WIDTH = 200
CARD_STANDART_HEIGHT = 300
CARD_SMALL_WIDTH = 33
CARD_SMALL_HEIGHT = 50
MAX_CARD_SIZE = 3.5
MIN_CARD_SIZE = 0.08

CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080

SCORE_CANVAS_WIDTH = 320
SCORE_CANVAS_HEIGHT = 180

TARGET_PATH = "target.png"

CARDS_MUTATIONS_COUNT = 4
CARDS_TOTAL_COUNT = 100
CARDS_WINNERS_COUNT = 20

GENERATIONS_PER_LOOP = 20

MAX_LOOP_COUNT = 10000

MUTATE_CARD_PROBABILITY = 0.35
MUTATE_SIZE_POWER = 0.15
MUTATE_ROTATION_POWER = 20
MUTATE_POSITION_POWER = 30
MUTATE_COLOR_POWER = 25


target_full = Image.open(TARGET_PATH).convert("RGB")
target_full = target_full.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.LANCZOS)

target_small = target_full.resize((SCORE_CANVAS_WIDTH, SCORE_CANVAS_HEIGHT), Image.LANCZOS)
target_small_arr = np.asarray(target_small, dtype=np.float32)

ERROR_WEIGHT_ARR = None
ERROR_FOCUS_STRENGTH = 6.0

CARD_IMAGES = {}
SCORE_CANVAS = Image.new("RGBA", (SCORE_CANVAS_WIDTH, SCORE_CANVAS_HEIGHT), (0, 0, 0, 255))

def createRandomCard():
    random_card_no = random.randrange(1, len(cards) + 1)
    
    new_card = {
        "card_no": random_card_no,
        "rotation": random.uniform(0, -360),
        "scale": random.uniform(MIN_CARD_SIZE, MAX_CARD_SIZE),
        "position": (random.randrange(-CARD_STANDART_WIDTH, CANVAS_WIDTH), random.randrange(-CARD_STANDART_HEIGHT, CANVAS_HEIGHT)),
        "tint": (255 + random.randrange(-40, 0), 255 + random.randrange(-40, 0), 255 + random.randrange(-40, 0))
    }
    
    new_card = ClampCardPosition(new_card)
    
    return new_card

def placeCard(canvas, card):
    base = CARD_IMAGES[card["card_no"]].copy()
    
    img = applyTint(base, card["tint"])
    
    img = img.resize((int(CARD_STANDART_WIDTH * card["scale"]), int(CARD_STANDART_HEIGHT * card["scale"])), Image.LANCZOS)
    img = img.rotate(card["rotation"], expand=True)
    
    canvas.paste(img, card["position"], img)

def placeSmallCard(canvas, card):
    base = CARD_IMAGES[card["card_no"]].copy()
    
    img = applyTint(base, card["tint"])
    
    img = img.resize((int(CARD_SMALL_WIDTH * card["scale"]), int(CARD_SMALL_HEIGHT * card["scale"])), Image.LANCZOS)
    img = img.rotate(card["rotation"], expand=True)
    
    sx = int(card["position"][0] / 6)
    sy = int(card["position"][1] / 6)
    
    canvas.paste(img, (sx, sy), img)
    
def renderOnCanvas(card_list, canvas):
    
    for card in card_list:
        placeCard(canvas, card)
    
    return canvas.convert("RGB")

def renderOnSmallCanvas(card_list, canvas):
    canvas.paste((0, 0, 0, 255), [0, 0, SCORE_CANVAS_WIDTH, SCORE_CANVAS_HEIGHT])
    
    for card in card_list:
        placeSmallCard(canvas, card)
    
    return canvas.convert("RGB")
    

def applyTint(img, tint):
    r, g, b = tint
    
    new_img = Image.new("RGBA", img.size, (r, g, b, 255))
    
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    alpha = img.split()[3]
    new_img.putalpha(alpha)
    
    return new_img

def mutateCard(card, return_count=CARDS_MUTATIONS_COUNT):
    new_cards = []
    
    for i in range(return_count):
        new_card = {}
        
        if random.random() < MUTATE_CARD_PROBABILITY:
            new_card_no = max(1, min(card["card_no"] + random.choice([-1, 1]), len(cards)))
            
            new_card["card_no"] = new_card_no
        else:
            new_card["card_no"] = card["card_no"]
        
        new_scale = card["scale"] + random.uniform(-MUTATE_SIZE_POWER, MUTATE_SIZE_POWER)
        new_scale = max(MIN_CARD_SIZE, min(MAX_CARD_SIZE, new_scale))
        new_card["scale"] = new_scale
        
        new_card["rotation"] = card["rotation"] + random.randrange(-MUTATE_ROTATION_POWER, MUTATE_ROTATION_POWER)
        new_card["position"] = (card["position"][0] + random.randrange(-MUTATE_POSITION_POWER, MUTATE_POSITION_POWER),
                                card["position"][1] + random.randrange(-MUTATE_POSITION_POWER, MUTATE_POSITION_POWER))
        
        r, g, b = card["tint"]
        
        r += random.randrange(-MUTATE_COLOR_POWER, MUTATE_COLOR_POWER)
        g += random.randrange(-MUTATE_COLOR_POWER, MUTATE_COLOR_POWER)
        b += random.randrange(-MUTATE_COLOR_POWER, MUTATE_COLOR_POWER)
        
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        new_card["tint"] = (r, g, b)
        
        new_card = ClampCardPosition(new_card)
        
        new_cards.append(new_card)
    
    return new_cards

def ClampCardPosition(card):
    x, y = card["position"]
    
    w = (CARD_STANDART_WIDTH * card["scale"])
    h = (CARD_STANDART_HEIGHT * card["scale"])
    
    x = max(0, min(CANVAS_WIDTH - w, x))
    y = max(0, min(CANVAS_HEIGHT - h, y))
    
    card["position"] = (int(x), int(y))
    
    return card

def calculateFitness(small_canvas, card):
    
    cand_small = small_canvas.copy()
    
    placeSmallCard(cand_small, card)
    cand_small_arr = np.asarray(cand_small, dtype=np.float32)
    
    diff = cand_small_arr - target_small_arr
    sq = diff ** 2
    
    if ERROR_WEIGHT_ARR is not None:
        sq *= ERROR_WEIGHT_ARR
    
    mse = np.mean(sq)
    
    color_score = 1.0 / (1.0 + mse / 5000.0)
    
    return color_score

def generationLoop(card_list):
    global ERROR_WEIGHT_ARR
    
    curent_small_canvas = Image.new("RGBA", (SCORE_CANVAS_WIDTH, SCORE_CANVAS_HEIGHT), (0, 0, 0, 255))
    curent_small_canvas = renderOnSmallCanvas(card_list, curent_small_canvas)
    curent_small_canvas_arr = np.asarray(curent_small_canvas, dtype=np.float32)
    
    difference = curent_small_canvas_arr - target_small_arr
    error = np.mean(difference ** 2, axis=2)
    
    max_error = np.max(error)
    if max_error > 0:
        normalized_error = error / max_error
    else:
        normalized_error = error
    
    ERROR_WEIGHT_ARR = 1.0 + ERROR_FOCUS_STRENGTH * normalized_error[..., np.newaxis]
    
    generation_cards = []
    
    for i in range(CARDS_TOTAL_COUNT):
        generation_cards.append(createRandomCard())
    
    for g in range(GENERATIONS_PER_LOOP):
        fitness_scores = {}
        
        for card_no in range(len(generation_cards)):
            fitness = calculateFitness(curent_small_canvas, generation_cards[card_no])
            fitness_scores[card_no] = fitness
        
        sorted_scores = sorted(fitness_scores.items(), key=lambda item: item[1], reverse=True)
        
        best_100_scores = sorted_scores[:CARDS_WINNERS_COUNT]
        
        best_100_cards = []
        
        for k, v in best_100_scores:
            best_100_cards.append(generation_cards[k])
            
        generation_cards = best_100_cards.copy()
        print("Generation:", g)
        if g < GENERATIONS_PER_LOOP - 1:
            for card in best_100_cards:
                generation_cards.extend(mutateCard(card, CARDS_MUTATIONS_COUNT))
    
    return generation_cards[0]

def mainLoop():
    card_list = []
    
    count = 0;
    
    while count < MAX_LOOP_COUNT:
        count += 1
        
        print("Loop count:", count)
        
        new_card = generationLoop(card_list)
        card_list.append(new_card)
        
        if count % 5 == 0:
            temp_saving = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 255))
            for card in card_list:
                placeCard(temp_saving, card)
        
            temp_saving.save("Results\\temp_save" + str(count) + ".png")
    
    result_canvas = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 255))
    for card in card_list:
        placeCard(result_canvas, card)
    
    result_canvas.show()
    result_canvas.save("Results\\result.png")

def loadCards():
    global CARD_IMAGES
    
    for id in cards.keys():
        CARD_IMAGES[id] = Image.open("Deck\\" + cards[id]).convert("RGBA")

loadCards()
mainLoop()
