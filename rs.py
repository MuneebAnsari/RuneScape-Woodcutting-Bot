import numpy as np
from PIL import ImageGrab
import cv2
from Inventory import Inventory
import pyautogui

# Define Trees as list of all trees detected
TREES = []


def locate_trees(image):
    """
        Locates trees on the game screen's current frame <image> and
        indicates that the trees have been found.

        @param image: The game screen's current frame
        @return: The game screen's frame with an outline around trees that have been detected
    """
    # Obtain gray scale of game screen frame <image>
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Obtain frame depicting all edges
    edge = cv2.Canny(image_gray, 300, 80)

    # MORPH_GRADIENT is the difference between the dilation and erosion of an image
    # Obtain outline of all objects in image using MORPH_GRADIENT
    kernel = np.ones((3, 3), np.uint8)
    gradient = cv2.morphologyEx(edge, cv2.MORPH_GRADIENT, kernel)

    # Obtain a frame where any small holes inside the foreground objects are closed using MORPH_CLOSE
    closed = cv2.morphologyEx(gradient, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))

    thresh = cv2.adaptiveThreshold(closed, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # Use RETR_TREE to get contours' parent-child relationships within hierarchy
    img, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through the outermost contour of all objects in frame and outline contours that most
    # resemble trees, that is, contours that are circular and of certain size.
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
    """
    Draws outline around circular contours

    @param image: The game screen's frame
    @param polynomial: polynomial representing a contour
    @param rectangle: Bounding rectangle for a tree
    @param x: top-left x coordinate
    @param y: top-left y coordinate
    @param width: width of rectangle
    @param length: length of rectangle
    @return: None
    """
    if len(polynomial) > 15:
        draw_outline(image, rectangle, x, y, width, length)


def draw_outline(image, rect, x, y, width, length):
    """
    Draws outline correctly based on size of contour found
    Adds outlined trees to list of all trees <TREES>

    @param image: The game screen's frame
    @param rect: Bounding rectangle for a tree
    @param x: top-left x coordinate
    @param y: top-left y coordinate
    @param width: width of rectangle
    @param length: length of rectangle
    @return None
    """
    if rect[2] < 60 and rect[3] < 60:
        cv2.rectangle(image, (x - 10, y - 30), (x + width + 15, y + length), (0, 255, 0), 2)
        cv2.putText(image, 'Tree', (x + width // 2, y + length // 2), 0, 0.4, (255, 255, 0))

    elif rect[2] < 100 and rect[3] < 100:
        cv2.rectangle(image, (x, y), (x + width, y + length), (0, 255, 0), 2)
        cv2.putText(image, 'Tree', (x + width // 2, y + length // 2), 0, 0.4, (255, 255, 0))

    x, y = pyautogui.center(rect)
    TREES.append((x, y))


def cut_trees(gs):
    """Cuts tree found in TREES"""
    for tree in TREES:
        pyautogui.doubleClick(tree[0] + 15, tree[1] + 40, 0.5)


def cut_next(bag):
    """Waits for player to finish cutting current"""
    if bag.num_logs != bag.num_logs + 1:
        cv2.waitKey(5000)


if __name__ == "__main__":

    # Loop for Bot
    while True:

        # Grab game screen image
        game_image = np.array(ImageGrab.grab((0, 40, 512, 370)))

        # Find trees on game screen
        processed_game_screen = locate_trees(game_image)
        cv2.imshow('RsBot', cv2.cvtColor(processed_game_screen, cv2.COLOR_BGR2RGB))

        # Grab inventory image
        inv_img = np.array(ImageGrab.grab((550, 240, 740, 500)))
        # Initialize inventory I
        the_inventory = Inventory(inv_img)
        # Update contents of inventory based on current status of inventory
        the_inventory.update()

        # Cut trees if there is space in the inventory otherwise drop contents of inventory
        if not the_inventory.is_full():
            cut_trees(processed_game_screen)

        elif the_inventory.is_full():
            the_inventory.drop_all_logs()

        print(the_inventory.num_logs)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
