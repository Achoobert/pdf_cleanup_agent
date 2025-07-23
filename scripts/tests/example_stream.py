import time
import sys

def main():
    for i in range(1, 31):
        print(i, flush=True)
        time.sleep(1)

if __name__ == '__main__':
    main() 