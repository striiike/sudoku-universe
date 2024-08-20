import win32gui
import win32ui
import win32con
from PIL import Image, ImageFilter
import pyautogui
import warnings        
import pytesseract
import numpy as np
from tqdm import tqdm
import copy

from sudoku_solver import SudokuSolver, brute_solve
import multiprocessing
import time
warnings.filterwarnings('ignore')


def capture_window_area(hwnd, x, y, width, height, name):
    # Create a device context and capture the window
    hwindc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(hwnd))
    hwnddc = hwindc.CreateCompatibleDC()
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hwindc, width, height)
    hwnddc.SelectObject(hbmp)

    hwnddc.BitBlt((0, 0), (width, height), hwindc, (x, y), win32con.SRCCOPY)
    
    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    img = Image.frombuffer("RGB", (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, "raw", "BGRX", 0, 1)
    img = img.convert("L")
    threshold_value = 128
    img = img.point(lambda x: 0 if x < threshold_value else 255)
    # img.save(f'{name}.png')

    width, height = img.size
    left, top, right, bottom = 10, 10, width - 10, height - 10
    img = img.crop((left, top, right, bottom)) 
    
    # Clean up
    hwnddc.DeleteDC()
    win32gui.DeleteObject(hbmp.GetHandle())

    return img


def annealing_solve(return_queue, solver, initial_grid):
    annealing_iterations = 5

    for i in range(annealing_iterations):
        grid = copy.deepcopy(initial_grid)
        solution, errors, masks = solver.start_annealing(grid)

        if errors == 0:
            print(f'solved in {i+1} annealing iterations')

            return_queue.put((solution, -1))

            return solution, errors

    return return_queue.put((solution, errors))


def brute_force_solve(return_queue, flat_grid):
    result = brute_solve(flat_grid)

    solution = [[] for _ in range(9)]
    for i in range(81):
        solution[i // 9].append(result[i])

    return return_queue.put((solution, -2))


if __name__ == '__main__':

    window_title = "Sudoku Universe"  
    hwnd = win32gui.FindWindow(None, window_title)  # Find the window by title

    if not hwnd:
        print("Window not found.")

    # Get the window's dimensions
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # Calculate the middle of the window
    middle_x = int(width // 2)
    middle_y = int(height // 2)

    out_flag = False
    for i in range(0, min(width, height) // 2, 15):
        _left = middle_x - i
        _top = middle_y - i

        precluded_colors = [
            (251, 251, 251), (250, 250, 250), (252, 252, 252),
            (233, 233, 233), (232, 232, 232), (234, 234, 234)]

        color_ref = win32gui.GetPixel(win32gui.GetWindowDC(hwnd), _left, _top)
        red, green, blue = color_ref & 0xff, (color_ref >> 8) & 0xff, (color_ref >> 16) & 0xff

        color = (red, green, blue)

        # print(f"left: {_left}, top: {_top} color: {color}")

        if color not in precluded_colors:
            if out_flag:
                break
            out_flag = True
        else:
            out_flag = False

    print(f"left: {_left}, top: {_top}")
    _left += 12
    _top += 12

    grid_width = (middle_x - _left) * 2
    grid_height = (middle_y - _top) * 2

    box_width = int(grid_width / 9)
    box_height = int(grid_height / 9)


    print(f"grid_width: {grid_width}, grid_height: {grid_height}")
    print(f"box_width: {box_width}, box_height: {box_height}")

    grid_cells = [[] for _ in range(9)]
    for i in range(9):  
        for j in range(9):
            # Capture the box
            img = capture_window_area(hwnd, _left + j * box_width, _top + i * box_height, box_width, box_height, f'./tmp/cell_{i}_{j}')
            grid_cells[i].append(img)



    initial_grid = [[] for _ in range(9)]

    with tqdm(total=81) as pbar:
        for i in range(9):
            for j in range(9):

                custom_config = r'--oem 3 --psm 6 outputbase digits'
                text = pytesseract.image_to_string(grid_cells[i][j], config=custom_config)
                text = ''.join([res for res in text if res.isdigit()])
                if not text:
                    initial_grid[i].append(0)
                else:
                    initial_grid[i].append(int(text))
                
                pbar.update(1)


    for r in initial_grid:
        print(r)

    print('solving sudoku...')


    solver = SudokuSolver(initial_grid)
    flat_grid = solver.flat_grid
    masks = solver.masks



    return_queue = multiprocessing.Queue()
    process1 = multiprocessing.Process(target=annealing_solve, args=(return_queue, solver, initial_grid))
    process2 = multiprocessing.Process(target=brute_force_solve, args=(return_queue, flat_grid))

    process1.start()
    process2.start()

    solution, errors = return_queue.get()
    def terminate_processes():
        process1.terminate()
        process2.terminate()

        process1.join()
        process2.join()
        
    if errors == -1:
        print(f'solved in annealing')
    elif errors == -2:
        print(f'solved in brute force')
    else:
        print(f'solved in brute force')
        solution, errors = return_queue.get()


    terminate_processes()
    for row in solution:
        print(row)

    for i in range(9):  
        for j in range(9):
            # move mouse to the cell and press number 3 using keyboard not writing just pressing the number
            if masks[i][j]:
                pyautogui.moveTo(_left + j * box_width + box_width // 2, _top + i * box_height + box_height // 2)
                pyautogui.typewrite(str(solution[i][j]))




