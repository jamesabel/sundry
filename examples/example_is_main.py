
def main(s):
    print(s)


# don't do this
if __name__ == "__main__":
    main("don't do this")

# do this
from sundry import is_main

if is_main():
    main("do this")
