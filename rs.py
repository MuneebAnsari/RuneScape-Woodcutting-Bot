import numpy as np
from PIL import ImageGrab
import cv2
from Inventory import Inventory
import pyautogui

TREES = []


def locate_trees(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edge = cv2.Canny(image_gray, 300, 80)
    kernel = np.ones((3, 3), np.uint8)
    gradient = cv2.morphologyEx(edge, cv2.MORPH_GRADIENT, kernel)
    closed = cv2.morphologyEx(gradient, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))

    thresh = cv2.adaptiveThreshold(closed, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    img, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # RETR_TREE to get contours' parent-child relationships within hierarchy

    for item in zip(contours, hierarchy[0]):
        c, h = item[0], item[1]
        # h[2] is the children of contour (negative then inner contour)
        # h[3] is the parents of contour  (negative that external contour)
        rectangle = cv2.boundingRect(c)
        x, y, width, length = rectangle

        if cv2.contourArea(c) > 500 and h[2] == -1:
            poly = cv2.approxPolyDP(c, 0.01 * cv2.arcLength(c, True), True)
            locate_circular_contour(image, poly, rectangle, x, y, width, length)

    return image


def locate_circular_contour(image, polynomial, rectangle, x, y, width, length):
    if len(polynomial) > 15:
        draw_outline(image, rectangle, x, y, width, length)


def draw_outline(image, rect, x, y, width, length):
    if rect[2] < 60 and rect[3] < 60:
        cv2.rectangle(image, (x - 10, y - 30), (x + width + 15, y + length), (0, 255, 0), 2)
        cv2.putText(image, 'Tree', (x + width // 2, y + length // 2), 0, 0.4, (255, 255, 0))

    elif rect[2] < 100 and rect[3] < 100:
        cv2.rectangle(image, (x, y), (x + width, y + length), (0, 255, 0), 2)
        cv2.putText(image, 'Tree', (x + width // 2, y + length // 2), 0, 0.4, (255, 255, 0))

    x, y = pyautogui.center(rect)
    TREES.append((x, y))


def cut_trees(gs):

    for tree in TREES:
        pyautogui.doubleClick(tree[0] + 15, tree[1] + 40, 0.5)


def cut_next(bag):
    if bag.num_logs != bag.num_logs + 1:
        cv2.waitKey(5000)


if __name__ == "__main__":

    while True:

        game_image = np.array(ImageGrab.grab((0, 40, 512, 370)))
        processed_game_screen = locate_trees(game_image)
        cv2.imshow('RsBot', cv2.cvtColor(processed_game_screen, cv2.COLOR_BGR2RGB))

        inv_img = np.array(ImageGrab.grab((550, 240, 740, 500)))
        the_inventory = Inventory(inv_img)
        the_inventory.update()

        if not the_inventory.is_full():
            cut_trees(processed_game_screen)

        elif the_inventory.is_full():
            the_inventory.drop_all_logs()

        print(the_inventory.num_logs)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
